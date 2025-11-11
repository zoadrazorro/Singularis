"""
Learning script with JSON progress tracking for webapp monitoring.
"""

import asyncio
import argparse
from pathlib import Path
import time
import json
from datetime import datetime

from singularis.llm import LMStudioClient, LMStudioConfig
from singularis.tier1_orchestrator import MetaOrchestratorLLM
from singularis.learning import TextProcessor
from singularis.tier3_neurons import NeuronSwarm, Lumen


async def process_chunk_with_progress(orchestrator, neuron_swarm, chunk, chunk_num, total_chunks, progress_file):
    """Process a single chunk and update progress file."""
    
    query = f"""Analyze this philosophical text:

Source: {chunk.source}
Section: {chunk.chunk_index + 1}/{chunk.total_chunks}

{chunk.text[:2000]}

Extract key philosophical concepts and insights."""
    
    start = time.time()
    
    try:
        # Process through orchestrator
        result = await orchestrator.process(query)
        
        # Learn in neuron swarm
        concepts = result['response'][:500]
        neuron_result = neuron_swarm.process_pattern(
            pattern=concepts,
            lumen_focus=Lumen.PARTICIPATUM,
            iterations=2,
        )
        
        elapsed = time.time() - start
        
        # Create chunk result
        chunk_result = {
            "chunk": chunk_num,
            "time": elapsed,
            "coherentia": result['synthesis']['coherentia'],
            "consciousness": result['synthesis']['consciousness'],
            "ethical": result['synthesis']['ethical_status'],
            "experts": result['experts_consulted'],
            "neurons_active": neuron_result['active_neurons'],
        }
        
        # Update progress file
        update_progress_file(progress_file, chunk_result, total_chunks)
        
        print(f"[{chunk_num}/{total_chunks}] Complete in {elapsed:.1f}s | C={result['synthesis']['coherentia']:.3f}")
        
        return chunk_result
        
    except Exception as e:
        print(f"[{chunk_num}/{total_chunks}] Error: {e}")
        return None


def update_progress_file(progress_file, chunk_result, total_chunks):
    """Update the progress JSON file."""
    
    # Load existing progress
    if progress_file.exists():
        with open(progress_file, 'r') as f:
            progress = json.load(f)
    else:
        progress = {
            "chunks": [],
            "total_chunks": total_chunks,
            "start_time": datetime.now().isoformat(),
        }
    
    # Add new chunk
    if chunk_result:
        progress["chunks"].append(chunk_result)
    
    # Calculate stats
    if progress["chunks"]:
        progress["chunks_completed"] = len(progress["chunks"])
        progress["avg_time"] = sum(c["time"] for c in progress["chunks"]) / len(progress["chunks"])
        progress["avg_coherentia"] = sum(c["coherentia"] for c in progress["chunks"]) / len(progress["chunks"])
        ethical_count = sum(1 for c in progress["chunks"] if c["ethical"])
        progress["ethical_rate"] = ethical_count / len(progress["chunks"])
        progress["last_update"] = datetime.now().isoformat()
    
    # Save
    with open(progress_file, 'w') as f:
        json.dump(progress, f, indent=2)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=240, help='Number of chunks to process')
    args = parser.parse_args()
    
    print("=" * 80)
    print("SINGULARIS LEARNING WITH PROGRESS TRACKING")
    print("=" * 80)
    
    # Paths
    project_root = Path(__file__).parent.parent
    philosophy_dir = project_root / "philosophy_texts"
    progress_file = project_root / "learning_progress.json"
    
    # Initialize
    config = LMStudioConfig(
        base_url="http://localhost:1234/v1",
        model_name="huihui-moe-60b-a38",
        temperature=0.7,
        max_tokens=1024,
    )
    
    async with LMStudioClient(config) as client:
        orchestrator = MetaOrchestratorLLM(
            llm_client=client,
            consciousness_threshold=0.65,
            coherentia_threshold=0.60,
            ethical_threshold=0.02,
        )
        
        neuron_swarm = NeuronSwarm(
            neurons_per_layer=6,
            learning_rate=0.05,
            activation_threshold=0.5,
        )
        
        # Load and chunk first text
        processor = TextProcessor(max_chunk_size=3000, overlap=200)
        first_file = philosophy_dir / "aristotle_nicomachean.txt"
        
        print(f"\nLoading: {first_file.name}")
        text = processor.load_text_file(first_file)
        chunks = processor.chunk_text(text, first_file.name)
        print(f"Total chunks: {len(chunks)}")
        print(f"Processing first {args.limit} chunks...")
        print(f"Progress file: {progress_file}")
        print("=" * 80)
        
        # Process chunks
        start_time = time.time()
        
        for i, chunk in enumerate(chunks[:args.limit]):
            await process_chunk_with_progress(
                orchestrator, neuron_swarm, chunk, i + 1, args.limit, progress_file
            )
        
        # Final summary
        elapsed = time.time() - start_time
        print("\n" + "=" * 80)
        print("LEARNING COMPLETE")
        print("=" * 80)
        print(f"Total time: {elapsed / 60:.1f} minutes")
        print(f"Progress saved to: {progress_file}")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
