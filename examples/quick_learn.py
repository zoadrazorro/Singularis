"""
Quick Learning Script with Real-Time Progress

Processes texts with immediate feedback and progress display.

Usage:
    python examples/quick_learn.py --limit 5
"""

import asyncio
import argparse
from pathlib import Path
from loguru import logger
import time

from singularis.llm import LMStudioClient, LMStudioConfig
from singularis.tier1_orchestrator import MetaOrchestratorLLM
from singularis.learning import TextProcessor
from singularis.tier3_neurons import NeuronSwarm, Lumen


async def process_chunk_simple(orchestrator, neuron_swarm, chunk, chunk_num, total_chunks):
    """Process a single chunk with simple output."""
    
    query = f"""Analyze this philosophical text:

Source: {chunk.source}
Section: {chunk.chunk_index + 1}/{chunk.total_chunks}

{chunk.text[:2000]}

Extract key philosophical concepts and insights."""
    
    print(f"\n[{chunk_num}/{total_chunks}] Processing {chunk.source} chunk {chunk.chunk_index + 1}...")
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
        
        # Display results
        print(f"  [OK] Complete in {elapsed:.1f}s")
        print(f"  Coherentia: {result['synthesis']['coherentia']:.3f}")
        print(f"  Consciousness: {result['synthesis']['consciousness']:.3f}")
        print(f"  Ethical: {result['synthesis']['ethical_status']}")
        print(f"  Neurons active: {neuron_result['active_neurons']}/18")
        print(f"  Experts: {', '.join(result['experts_consulted'])}")
        
        return result
        
    except Exception as e:
        print(f"  [ERROR] {e}")
        return None


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=5, help='Number of chunks to process')
    args = parser.parse_args()
    
    print("=" * 80)
    print("SINGULARIS QUICK LEARNING")
    print("=" * 80)
    print(f"Processing {args.limit} chunks from Aristotle's Nicomachean Ethics")
    print("=" * 80)
    
    # Paths
    project_root = Path(__file__).parent.parent
    philosophy_dir = project_root / "philosophy_texts"
    
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
        print(f"Size: {len(text):,} characters")
        
        chunks = processor.chunk_text(text, first_file.name)
        print(f"Chunks: {len(chunks)}")
        print(f"Processing first {args.limit} chunks...")
        
        # Process chunks
        start_time = time.time()
        results = []
        
        for i, chunk in enumerate(chunks[:args.limit]):
            result = await process_chunk_simple(
                orchestrator, neuron_swarm, chunk, i + 1, args.limit
            )
            if result:
                results.append(result)
        
        # Summary
        elapsed = time.time() - start_time
        
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Chunks processed: {len(results)}")
        print(f"Total time: {elapsed / 60:.1f} minutes")
        print(f"Avg time/chunk: {elapsed / len(results):.1f} seconds")
        
        if results:
            avg_coherentia = sum(r['synthesis']['coherentia'] for r in results) / len(results)
            ethical_count = sum(1 for r in results if r['synthesis']['ethical_status'])
            
            print(f"Avg coherentia: {avg_coherentia:.3f}")
            print(f"Ethical rate: {ethical_count}/{len(results)} ({ethical_count/len(results)*100:.0f}%)")
        
        # Neuron stats
        swarm_stats = neuron_swarm.get_statistics()
        print(f"\nNeuron swarm:")
        print(f"  Connections: {swarm_stats['total_connections']}")
        print(f"  Patterns learned: {swarm_stats['patterns_learned']}")
        print(f"  Avg connections/neuron: {swarm_stats['avg_connections_per_neuron']:.1f}")
        
        print("\n" + "=" * 80)
        print("Learning complete!")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
