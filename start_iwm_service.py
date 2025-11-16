"""
Start IWM Vision World Model Service

Simple wrapper to start the IWM FastAPI service with sane defaults.

Usage:
    python start_iwm_service.py
    python start_iwm_service.py --port 8001 --device cuda:0
    python start_iwm_service.py --model_path ./checkpoints/iwm/iwm_core_final.pt
"""

import os
import sys
import argparse
from loguru import logger


def main():
    parser = argparse.ArgumentParser(description="Start IWM Service")
    
    parser.add_argument('--variant', type=str, default='core',
                        choices=['core', 'invariant', 'equivariant'],
                        help='Model variant')
    parser.add_argument('--model_path', type=str, default=None,
                        help='Path to model checkpoint (optional)')
    parser.add_argument('--device', type=str, default='cuda',
                        help='Device (cuda, cuda:0, cpu)')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                        help='Service host')
    parser.add_argument('--port', type=int, default=8001,
                        help='Service port')
    
    args = parser.parse_args()
    
    # Set environment variables
    os.environ['IWM_MODEL_VARIANT'] = args.variant
    os.environ['IWM_DEVICE'] = args.device
    os.environ['IWM_SERVICE_HOST'] = args.host
    os.environ['IWM_SERVICE_PORT'] = str(args.port)
    
    if args.model_path:
        if not os.path.exists(args.model_path):
            logger.error(f"Model checkpoint not found: {args.model_path}")
            sys.exit(1)
        os.environ['IWM_MODEL_PATH'] = args.model_path
        logger.info(f"Using checkpoint: {args.model_path}")
    else:
        logger.warning("No checkpoint provided - using random weights (for testing only)")
    
    logger.info(f"Starting IWM service: {args.variant} on {args.device}")
    logger.info(f"Service will be available at http://{args.host}:{args.port}")
    
    # Import and run service
    from singularis.world_model.iwm_service import main as service_main
    service_main()


if __name__ == "__main__":
    main()
