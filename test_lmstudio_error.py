"""Test script to reproduce LM Studio 400 error."""

import asyncio
from singularis.llm.lmstudio_client import LMStudioClient, LMStudioConfig


async def test_lmstudio_client():
    """Test LM Studio client with various configurations."""
    
    # Test 1: Mistral with system prompt
    print("=" * 60)
    print("Test 1: Mistral-7B with system prompt")
    print("=" * 60)
    config1 = LMStudioConfig(
        model_name="mistralai/mistral-7b-instruct-v0.3",
        max_tokens=200
    )
    client1 = LMStudioClient(config1)
    
    try:
        result = await client1.generate(
            prompt="What action should I take?",
            system_prompt="You are a Skyrim AI tactical advisor."
        )
        print(f"[SUCCESS] {result['content'][:100]}...")
    except Exception as e:
        print(f"[FAILED] {e}")
    finally:
        await client1.close()
    
    # Test 2: Qwen3-4B thinking model
    print("\n" + "=" * 60)
    print("Test 2: Qwen3-4B thinking model")
    print("=" * 60)
    config2 = LMStudioConfig(
        model_name="qwen/qwen3-4b-thinking-2507",
        max_tokens=200,
        timeout=30
    )
    client2 = LMStudioClient(config2)
    
    try:
        result = await client2.generate(
            prompt="What action should I take?",
            system_prompt="You are a Skyrim AI tactical advisor."
        )
        print(f"[SUCCESS] {result['content'][:100]}...")
    except Exception as e:
        print(f"[FAILED] {e}")
    finally:
        await client2.close()
    
    # Test 3: Phi-4 (like the actual system uses)
    print("\n" + "=" * 60)
    print("Test 3: Phi-4 mini reasoning")
    print("=" * 60)
    config3 = LMStudioConfig(
        model_name="microsoft/phi-4-mini-reasoning",
        max_tokens=200
    )
    client3 = LMStudioClient(config3)
    
    try:
        result = await client3.generate(
            prompt="Recommend an action: jump, activate, or move_forward",
            system_prompt="You are a Skyrim AI. Respond with: ACTION: [name]"
        )
        print(f"[SUCCESS] {result['content'][:100]}...")
    except Exception as e:
        print(f"[FAILED] {e}")
    finally:
        await client3.close()


if __name__ == "__main__":
    asyncio.run(test_lmstudio_client())
