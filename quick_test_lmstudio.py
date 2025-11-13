"""Quick test for the system prompt fix."""

import asyncio
from singularis.llm.lmstudio_client import LMStudioClient, LMStudioConfig


async def quick_test():
    print("Testing Mistral-7B with system prompt...")
    config = LMStudioConfig(
        model_name="mistralai/mistral-7b-instruct-v0.3",
        max_tokens=100,
        timeout=10
    )
    client = LMStudioClient(config)
    
    try:
        result = await client.generate(
            prompt="Recommend ONE action from: jump, activate, move_forward",
            system_prompt="You are a Skyrim AI. Be very brief."
        )
        print(f"SUCCESS: {result['content']}")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False
    finally:
        await client.close()


if __name__ == "__main__":
    success = asyncio.run(quick_test())
    exit(0 if success else 1)
