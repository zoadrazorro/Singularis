"""
Test Script for Local-Only LLM Architecture

Verifies that Singularis LifeOps works in local-only mode with
all LLM traffic routed to local LM Studio endpoint.

Usage:
    export SINGULARIS_LOCAL_ONLY=1
    export OPENAI_BASE_URL="http://192.168.1.100:1234/v1"
    python test_local_only_llm.py
"""

import asyncio
import sys
import os
from typing import Optional

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_header(text: str):
    """Print formatted header."""
    print(f"\n{BLUE}{'=' * 70}{RESET}")
    print(f"{BLUE}{text.center(70)}{RESET}")
    print(f"{BLUE}{'=' * 70}{RESET}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{GREEN}✓{RESET} {text}")


def print_error(text: str):
    """Print error message."""
    print(f"{RED}✗{RESET} {text}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{YELLOW}⚠{RESET} {text}")


def print_info(text: str):
    """Print info message."""
    print(f"  {text}")


async def test_1_runtime_flags():
    """Test 1: Runtime flags configuration."""
    print_header("TEST 1: Runtime Flags Configuration")
    
    try:
        from singularis.core.runtime_flags import (
            LOCAL_ONLY_LLM,
            NODE_ROLE,
            get_runtime_info,
            is_local_url
        )
        
        info = get_runtime_info()
        
        print_info(f"LOCAL_ONLY_LLM: {info['local_only_llm']}")
        print_info(f"NODE_ROLE: {info['node_role']}")
        print_info(f"SINGULARIS_LOCAL_ONLY env: {info['singularis_local_only_env']}")
        print_info(f"NODE_ROLE env: {info['node_role_env']}")
        
        # Test is_local_url function
        test_cases = [
            ("http://localhost:1234/v1", True),
            ("http://127.0.0.1:1234/v1", True),
            ("http://192.168.1.100:1234/v1", True),
            ("http://10.0.0.50:1234/v1", True),
            ("https://api.openai.com/v1", False),
            ("https://api.anthropic.com/v1", False),
        ]
        
        print_info("\nTesting is_local_url():")
        all_passed = True
        for url, expected in test_cases:
            result = is_local_url(url)
            status = "✓" if result == expected else "✗"
            print_info(f"  {status} {url}: {result} (expected {expected})")
            if result != expected:
                all_passed = False
        
        if all_passed:
            print_success("Runtime flags test passed")
            return True
        else:
            print_error("Runtime flags test failed (is_local_url issues)")
            return False
            
    except Exception as e:
        print_error(f"Runtime flags test failed: {e}")
        return False


async def test_2_openai_client():
    """Test 2: OpenAIClient with local endpoint."""
    print_header("TEST 2: OpenAIClient Local Endpoint")
    
    try:
        from singularis.llm.openai_client import OpenAIClient
        
        # Get endpoint from environment
        base_url = os.getenv("OPENAI_BASE_URL", "http://localhost:1234/v1")
        print_info(f"Testing endpoint: {base_url}")
        
        # Create client
        client = OpenAIClient(
            model="microsoft/phi-4-mini-reasoning",
            base_url=base_url
        )
        
        print_info(f"Client base_url: {client.base_url}")
        print_info(f"Client model: {client.model}")
        print_info(f"Client available: {client.is_available()}")
        
        if not client.is_available():
            print_warning("Client not available - check OPENAI_BASE_URL")
            return False
        
        # Test generation (with timeout)
        print_info("\nTesting generation...")
        try:
            result = await asyncio.wait_for(
                client.generate_text("Say 'test successful' if you can read this."),
                timeout=30.0
            )
            
            print_info(f"Response length: {len(result)} chars")
            print_info(f"Response preview: {result[:100]}...")
            
            await client.close()
            print_success("OpenAIClient test passed")
            return True
            
        except asyncio.TimeoutError:
            print_error("Generation timed out - is LM Studio running?")
            await client.close()
            return False
            
    except Exception as e:
        print_error(f"OpenAIClient test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_3_unified_consciousness():
    """Test 3: UnifiedConsciousnessLayer with local endpoint."""
    print_header("TEST 3: UnifiedConsciousnessLayer Local Mode")
    
    try:
        from singularis.unified_consciousness_layer import UnifiedConsciousnessLayer
        
        # Get endpoint from environment
        base_url = os.getenv("OPENAI_BASE_URL", "http://localhost:1234/v1")
        print_info(f"Creating layer with endpoint: {base_url}")
        
        # Create layer
        layer = UnifiedConsciousnessLayer(
            gpt5_model="microsoft/phi-4-mini-reasoning",
            gpt5_nano_model="microsoft/phi-4-mini-reasoning",
            openai_base_url=base_url,
            local_only=True
        )
        
        print_info(f"Layer local_only: {layer.local_only}")
        print_info(f"Layer endpoint: {layer.openai_base_url}")
        print_info(f"GPT-5 client available: {layer.gpt5_client.is_available()}")
        
        if not layer.gpt5_client.is_available():
            print_error("GPT-5 client not available")
            return False
        
        # Test processing (with reduced scope)
        print_info("\nTesting consciousness processing...")
        try:
            result = await asyncio.wait_for(
                layer.process(
                    query="What is 2+2?",
                    subsystem_inputs={
                        'llm': "Simple arithmetic test",
                    }
                ),
                timeout=60.0
            )
            
            print_info(f"Response length: {len(result.response)} chars")
            print_info(f"Coherence score: {result.coherence_score:.2f}")
            print_info(f"Total time: {result.total_time:.2f}s")
            print_info(f"Nano experts: {len(result.nano_expert_responses)}")
            
            await layer.close()
            print_success("UnifiedConsciousnessLayer test passed")
            return True
            
        except asyncio.TimeoutError:
            print_error("Processing timed out")
            await layer.close()
            return False
            
    except Exception as e:
        print_error(f"UnifiedConsciousnessLayer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_4_agi_orchestrator():
    """Test 4: AGIOrchestrator integration."""
    print_header("TEST 4: AGIOrchestrator Integration")
    
    try:
        from singularis.agi_orchestrator import AGIOrchestrator, AGIConfig
        
        # Get endpoint from environment
        base_url = os.getenv("OPENAI_BASE_URL", "http://localhost:1234/v1")
        print_info(f"Creating orchestrator with endpoint: {base_url}")
        
        # Create config
        config = AGIConfig(
            lm_studio_url=base_url,
            lm_studio_model="microsoft/phi-4-mini-reasoning",
            use_unified_consciousness=True,
            gpt5_model="microsoft/phi-4-mini-reasoning",
            gpt5_nano_model="microsoft/phi-4-mini-reasoning",
            use_emotion_system=False,  # Skip emotion for speed
        )
        
        print_info("Initializing orchestrator...")
        orchestrator = AGIOrchestrator(config)
        
        print_info("Initializing LLM...")
        await orchestrator.initialize_llm()
        
        # Check unified consciousness
        if orchestrator.unified_consciousness is None:
            print_error("Unified consciousness not initialized")
            return False
        
        print_info(f"Unified consciousness mode: {'LOCAL-ONLY' if orchestrator.unified_consciousness.local_only else 'CLOUD'}")
        print_info(f"Unified consciousness endpoint: {orchestrator.unified_consciousness.openai_base_url}")
        
        # Quick test query
        print_info("\nTesting consciousness query...")
        try:
            result = await asyncio.wait_for(
                orchestrator.unified_consciousness.process(
                    query="Test query: What is your purpose?",
                    subsystem_inputs={'llm': "Testing integration"}
                ),
                timeout=60.0
            )
            
            print_info(f"Response length: {len(result.response)} chars")
            print_info(f"Coherence: {result.coherence_score:.2f}")
            
            print_success("AGIOrchestrator test passed")
            return True
            
        except asyncio.TimeoutError:
            print_error("Query timed out")
            return False
            
    except Exception as e:
        print_error(f"AGIOrchestrator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_5_local_only_enforcement():
    """Test 5: LOCAL_ONLY_LLM enforcement."""
    print_header("TEST 5: Local-Only Mode Enforcement")
    
    try:
        from singularis.unified_consciousness_layer import UnifiedConsciousnessLayer
        
        print_info("Testing cloud URL rejection in local-only mode...")
        
        # This should raise an error
        layer = UnifiedConsciousnessLayer(
            gpt5_model="gpt-4o",
            openai_base_url="https://api.openai.com/v1",  # Cloud URL
            local_only=True  # Enforce local-only
        )
        
        try:
            # This should fail
            result = await layer.process(
                query="This should fail",
                subsystem_inputs={'llm': 'test'}
            )
            
            print_error("ERROR: Cloud URL was not rejected!")
            return False
            
        except RuntimeError as e:
            if "LOCAL_ONLY mode" in str(e):
                print_success("Cloud URL correctly rejected in local-only mode")
                print_info(f"Error message: {str(e)[:100]}...")
                return True
            else:
                print_error(f"Wrong error: {e}")
                return False
                
    except Exception as e:
        print_error(f"Enforcement test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print_header("SINGULARIS LOCAL-ONLY LLM TEST SUITE")
    
    # Check environment
    print_info("Environment Check:")
    local_only = os.getenv("SINGULARIS_LOCAL_ONLY", "not set")
    base_url = os.getenv("OPENAI_BASE_URL", "not set")
    node_role = os.getenv("NODE_ROLE", "not set")
    
    print_info(f"  SINGULARIS_LOCAL_ONLY: {local_only}")
    print_info(f"  OPENAI_BASE_URL: {base_url}")
    print_info(f"  NODE_ROLE: {node_role}")
    
    if local_only != "1":
        print_warning("SINGULARIS_LOCAL_ONLY is not set to '1'")
        print_warning("Some tests may behave unexpectedly")
    
    if base_url == "not set":
        print_warning("OPENAI_BASE_URL is not set")
        print_warning("Will use default: http://localhost:1234/v1")
    
    # Run tests
    results = {}
    
    results['test_1'] = await test_1_runtime_flags()
    results['test_2'] = await test_2_openai_client()
    results['test_3'] = await test_3_unified_consciousness()
    results['test_4'] = await test_4_agi_orchestrator()
    results['test_5'] = await test_5_local_only_enforcement()
    
    # Summary
    print_header("TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    for test_name, result in results.items():
        status = f"{GREEN}PASSED{RESET}" if result else f"{RED}FAILED{RESET}"
        print(f"  {test_name}: {status}")
    
    print(f"\n{BLUE}Total:{RESET} {total} tests")
    print(f"{GREEN}Passed:{RESET} {passed}")
    print(f"{RED}Failed:{RESET} {failed}")
    
    if passed == total:
        print(f"\n{GREEN}{'=' * 70}{RESET}")
        print(f"{GREEN}✓ ALL TESTS PASSED - Local-only LLM architecture verified!{RESET}")
        print(f"{GREEN}{'=' * 70}{RESET}\n")
        return 0
    else:
        print(f"\n{RED}{'=' * 70}{RESET}")
        print(f"{RED}✗ SOME TESTS FAILED - Check configuration{RESET}")
        print(f"{RED}{'=' * 70}{RESET}\n")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
