"""
Train IWM Phase 1 - Core World Model

Trains ViT-B/16 + 8-layer predictor on:
- ImageNet-style images (50%)
- Skyrim screenshots (50%)

Target hardware: 2x AMD 7900 XT (20GB each)
Training time: ~24-36 hours for 100 epochs

Usage:
    # Single GPU
    python train_iwm_phase1.py --device cuda:0 --batch_size 160
    
    # Multi-GPU (DDP)
    python -m torch.distributed.launch --nproc_per_node=2 train_iwm_phase1.py --ddp
"""

import os
import argparse
import time
from pathlib import Path
from typing import Dict, Any, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, DistributedSampler
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

import numpy as np
from PIL import Image
from torchvision import transforms
from loguru import logger

from singularis.world_model.iwm_models import IWM, IWMConfig, create_iwm_model


# ========================================
# Dataset with Augmentations (JEPA-style)
# ========================================

class IWMAugmentedDataset(Dataset):
    """
    Dataset that applies asymmetric augmentations for IWM training.
    
    For each image, generates:
    - x: weakly augmented (source)
    - x_aug: strongly augmented (target)
    - aug_params: parameters describing the transformation
    """
    
    def __init__(
        self,
        image_paths: list,
        image_size: int = 224,
        aug_dim: int = 16
    ):
        self.image_paths = image_paths
        self.image_size = image_size
        self.aug_dim = aug_dim
        
        # Weak augmentation (source)
        self.transform_weak = transforms.Compose([
            transforms.Resize(image_size + 32, interpolation=transforms.InterpolationMode.BICUBIC),
            transforms.RandomCrop(image_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        # Strong augmentation (target)
        self.transform_strong = transforms.Compose([
            transforms.Resize(image_size + 32, interpolation=transforms.InterpolationMode.BICUBIC),
            transforms.RandomResizedCrop(image_size, scale=(0.6, 1.0)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.ColorJitter(brightness=0.4, contrast=0.4, saturation=0.4, hue=0.1),
            transforms.RandomGrayscale(p=0.2),
            transforms.GaussianBlur(kernel_size=23, sigma=(0.1, 2.0)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        # Load image
        img_path = self.image_paths[idx]
        try:
            img = Image.open(img_path).convert('RGB')
        except Exception as e:
            logger.warning(f"Failed to load {img_path}: {e}, using blank")
            img = Image.new('RGB', (self.image_size, self.image_size), color='gray')
        
        # Apply augmentations
        x = self.transform_weak(img)
        x_aug = self.transform_strong(img)
        
        # Generate augmentation parameters (simplified)
        # In practice, you'd encode actual transform parameters
        aug_params = torch.randn(self.aug_dim) * 0.1
        
        return x, x_aug, aug_params


def collect_image_paths(data_dir: str, extensions: tuple = ('.jpg', '.jpeg', '.png')) -> list:
    """Recursively collect image paths."""
    data_path = Path(data_dir)
    image_paths = []
    
    for ext in extensions:
        image_paths.extend(list(data_path.rglob(f'*{ext}')))
    
    logger.info(f"Found {len(image_paths)} images in {data_dir}")
    return [str(p) for p in image_paths]


# ========================================
# Training Loop
# ========================================

def train_epoch(
    model: IWM,
    dataloader: DataLoader,
    optimizer: torch.optim.Optimizer,
    scheduler: torch.optim.lr_scheduler._LRScheduler,
    epoch: int,
    device: str,
    rank: int = 0,
    world_size: int = 1
) -> Dict[str, float]:
    """Train one epoch."""
    model.train()
    
    total_loss = 0.0
    total_loss_cls = 0.0
    total_loss_patches = 0.0
    num_batches = 0
    
    for batch_idx, (x, x_aug, aug_params) in enumerate(dataloader):
        x = x.to(device)
        x_aug = x_aug.to(device)
        aug_params = aug_params.to(device)
        
        # Forward
        outputs = model(x, x_aug, aug_params)
        loss = outputs['loss']
        
        # Backward
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        scheduler.step()
        
        # Update EMA
        model.module.update_ema() if hasattr(model, 'module') else model.update_ema()
        
        # Stats
        total_loss += loss.item()
        total_loss_cls += outputs['loss_cls'].item()
        total_loss_patches += outputs['loss_patches'].item()
        num_batches += 1
        
        # Log
        if rank == 0 and batch_idx % 50 == 0:
            logger.info(
                f"Epoch {epoch} | Batch {batch_idx}/{len(dataloader)} | "
                f"Loss: {loss.item():.4f} | "
                f"CLS: {outputs['loss_cls'].item():.4f} | "
                f"Patches: {outputs['loss_patches'].item():.4f} | "
                f"LR: {scheduler.get_last_lr()[0]:.6f}"
            )
    
    return {
        'loss': total_loss / num_batches,
        'loss_cls': total_loss_cls / num_batches,
        'loss_patches': total_loss_patches / num_batches
    }


@torch.no_grad()
def validate(
    model: IWM,
    dataloader: DataLoader,
    device: str,
    rank: int = 0
) -> Dict[str, float]:
    """Validate model."""
    model.eval()
    
    total_loss = 0.0
    total_loss_cls = 0.0
    total_loss_patches = 0.0
    num_batches = 0
    
    for x, x_aug, aug_params in dataloader:
        x = x.to(device)
        x_aug = x_aug.to(device)
        aug_params = aug_params.to(device)
        
        outputs = model(x, x_aug, aug_params)
        
        total_loss += outputs['loss'].item()
        total_loss_cls += outputs['loss_cls'].item()
        total_loss_patches += outputs['loss_patches'].item()
        num_batches += 1
    
    return {
        'loss': total_loss / num_batches,
        'loss_cls': total_loss_cls / num_batches,
        'loss_patches': total_loss_patches / num_batches
    }


def save_checkpoint(
    model: IWM,
    optimizer: torch.optim.Optimizer,
    scheduler: torch.optim.lr_scheduler._LRScheduler,
    epoch: int,
    path: str
):
    """Save training checkpoint."""
    state_dict = model.module.state_dict() if hasattr(model, 'module') else model.state_dict()
    
    torch.save({
        'epoch': epoch,
        'model': state_dict,
        'optimizer': optimizer.state_dict(),
        'scheduler': scheduler.state_dict(),
    }, path)
    
    logger.info(f"Checkpoint saved: {path}")


# ========================================
# Main Training Script
# ========================================

def main(args):
    # DDP setup
    if args.ddp:
        dist.init_process_group(backend='nccl')
        rank = dist.get_rank()
        world_size = dist.get_world_size()
        torch.cuda.set_device(rank)
        device = f'cuda:{rank}'
        logger.info(f"[Rank {rank}/{world_size}] Initialized DDP")
    else:
        rank = 0
        world_size = 1
        device = args.device
        logger.info(f"Single GPU training on {device}")
    
    # Create model
    model = create_iwm_model(variant='core', device=device)
    
    if args.ddp:
        model = DDP(model, device_ids=[rank], find_unused_parameters=False)
    
    # Collect dataset
    image_paths = []
    for data_dir in args.data_dirs:
        if os.path.exists(data_dir):
            image_paths.extend(collect_image_paths(data_dir))
        else:
            logger.warning(f"Data directory not found: {data_dir}")
    
    if len(image_paths) == 0:
        logger.error("No images found! Please provide valid data directories.")
        return
    
    # Split train/val
    np.random.shuffle(image_paths)
    split_idx = int(len(image_paths) * 0.95)
    train_paths = image_paths[:split_idx]
    val_paths = image_paths[split_idx:]
    
    logger.info(f"Train: {len(train_paths)} | Val: {len(val_paths)}")
    
    # Create datasets
    train_dataset = IWMAugmentedDataset(train_paths, image_size=224)
    val_dataset = IWMAugmentedDataset(val_paths, image_size=224)
    
    # Create dataloaders
    if args.ddp:
        train_sampler = DistributedSampler(train_dataset, num_replicas=world_size, rank=rank, shuffle=True)
        train_loader = DataLoader(
            train_dataset,
            batch_size=args.batch_size,
            sampler=train_sampler,
            num_workers=args.num_workers,
            pin_memory=True
        )
    else:
        train_loader = DataLoader(
            train_dataset,
            batch_size=args.batch_size,
            shuffle=True,
            num_workers=args.num_workers,
            pin_memory=True
        )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=True
    )
    
    # Optimizer & scheduler
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=args.lr,
        weight_decay=args.weight_decay,
        betas=(0.9, 0.999)
    )
    
    total_steps = args.epochs * len(train_loader)
    warmup_steps = int(0.1 * total_steps)
    
    scheduler = torch.optim.lr_scheduler.OneCycleLR(
        optimizer,
        max_lr=args.lr,
        total_steps=total_steps,
        pct_start=0.1,
        anneal_strategy='cos'
    )
    
    # Training loop
    os.makedirs(args.checkpoint_dir, exist_ok=True)
    
    for epoch in range(1, args.epochs + 1):
        if args.ddp:
            train_sampler.set_epoch(epoch)
        
        # Train
        train_metrics = train_epoch(
            model, train_loader, optimizer, scheduler,
            epoch, device, rank, world_size
        )
        
        if rank == 0:
            logger.info(f"Epoch {epoch} Train: {train_metrics}")
        
        # Validate
        if epoch % args.val_every == 0:
            val_metrics = validate(model, val_loader, device, rank)
            if rank == 0:
                logger.info(f"Epoch {epoch} Val: {val_metrics}")
        
        # Save checkpoint
        if rank == 0 and epoch % args.save_every == 0:
            checkpoint_path = os.path.join(
                args.checkpoint_dir,
                f"iwm_core_epoch{epoch}.pt"
            )
            save_checkpoint(model, optimizer, scheduler, epoch, checkpoint_path)
    
    # Final checkpoint
    if rank == 0:
        final_path = os.path.join(args.checkpoint_dir, "iwm_core_final.pt")
        save_checkpoint(model, optimizer, scheduler, args.epochs, final_path)
        logger.info("Training complete!")
    
    if args.ddp:
        dist.destroy_process_group()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train IWM Phase 1")
    
    # Data
    parser.add_argument('--data_dirs', nargs='+', default=['./data/imagenet', './data/skyrim'],
                        help='Directories containing images')
    
    # Model
    parser.add_argument('--device', type=str, default='cuda',
                        help='Device (cuda, cuda:0, cpu)')
    
    # Training
    parser.add_argument('--batch_size', type=int, default=160,
                        help='Batch size per GPU')
    parser.add_argument('--epochs', type=int, default=100,
                        help='Number of epochs')
    parser.add_argument('--lr', type=float, default=4e-4,
                        help='Learning rate')
    parser.add_argument('--weight_decay', type=float, default=0.05,
                        help='Weight decay')
    parser.add_argument('--num_workers', type=int, default=4,
                        help='Dataloader workers')
    
    # DDP
    parser.add_argument('--ddp', action='store_true',
                        help='Use DistributedDataParallel')
    
    # Checkpointing
    parser.add_argument('--checkpoint_dir', type=str, default='./checkpoints/iwm',
                        help='Checkpoint directory')
    parser.add_argument('--save_every', type=int, default=10,
                        help='Save checkpoint every N epochs')
    parser.add_argument('--val_every', type=int, default=5,
                        help='Validate every N epochs')
    
    args = parser.parse_args()
    
    main(args)
