"""
Test Streaming Video Interpreter with Gemini 2.5 Flash Native Audio.

This demonstrates real-time video analysis with spoken commentary.
"""

import asyncio
from PIL import Image
from singularis.perception import StreamingVideoInterpreter, InterpretationMode


async def interpretation_callback(interpretation):
    """Callback for new interpretations."""
    print(f"\n[FRAME {interpretation.frame_number}] {interpretation.mode.value.upper()}")
    print(f"[TEXT] {interpretation.text}")
    print(f"[AUDIO] {len(interpretation.audio_data) if interpretation.audio_data else 0} bytes")
    print(f"[CONFIDENCE] {interpretation.confidence:.2f}")


async def main():
    print("="*70)
    print("STREAMING VIDEO INTERPRETER TEST")
    print("="*70)
    print()
    
    # Initialize interpreter
    interpreter = StreamingVideoInterpreter(
        mode=InterpretationMode.COMPREHENSIVE,
        frame_rate=0.5,  # Analyze 1 frame every 2 seconds
        audio_enabled=True,
        voice="Kore"
    )
    
    # Set callback
    interpreter.on_interpretation = interpretation_callback
    
    print("[INTERPRETER] Initialized")
    print(f"[MODE] {interpreter.mode.value}")
    print(f"[AUDIO] {'Enabled' if interpreter.audio_enabled else 'Disabled'}")
    print()
    
    try:
        # Start streaming
        await interpreter.start_streaming()
        print("[STREAMING] Started")
        print()
        
        # Simulate adding frames (in real use, these come from screen capture)
        print("[TEST] Adding test frames...")
        print("(In production, frames come from screen capture)")
        print()
        
        # Create a dummy image for testing
        test_image = Image.new('RGB', (800, 600), color='blue')
        
        # Add frames
        for i in range(3):
            print(f"[FRAME {i}] Adding frame...")
            await interpreter.add_frame(test_image, scene_type="combat")
            
            # Wait for processing
            await asyncio.sleep(3)
        
        # Stop streaming
        await interpreter.stop_streaming()
        print()
        print("[STREAMING] Stopped")
        
        # Show statistics
        stats = interpreter.get_stats()
        print()
        print("="*70)
        print("INTERPRETER STATISTICS")
        print("="*70)
        print(f"Mode: {stats['mode']}")
        print(f"Total frames: {stats['total_frames']}")
        print(f"Total interpretations: {stats['total_interpretations']}")
        print(f"Buffer size: {stats['buffer_size']}")
        print(f"Audio enabled: {stats['audio_enabled']}")
        print(f"Voice: {stats['voice']}")
        
    finally:
        await interpreter.close()
        print()
        print("[INTERPRETER] Closed")


if __name__ == "__main__":
    print("NOTE: This test requires:")
    print("  1. GEMINI_API_KEY environment variable")
    print("  2. pygame installed (pip install pygame)")
    print("  3. Active internet connection")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nTest failed: {e}")
        import traceback
        traceback.print_exc()
