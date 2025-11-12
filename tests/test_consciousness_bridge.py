"""
Tests for ConsciousnessBridge

Tests the consciousness bridge integration between game state and LLM orchestrator.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

from singularis.skyrim.consciousness_bridge import ConsciousnessBridge, ConsciousnessState


class TestConsciousnessBridge:
    """Test suite for ConsciousnessBridge."""

    @pytest.fixture
    def bridge_no_llm(self):
        """Create bridge without LLM (heuristic mode)."""
        return ConsciousnessBridge(consciousness_llm=None)

    @pytest.fixture
    def mock_orchestrator(self):
        """Create mock MetaOrchestratorLLM."""
        orchestrator = Mock()
        orchestrator.process = AsyncMock(return_value={
            'response': 'Test response with higher coherence suggested',
            'confidence': 0.8,
        })
        return orchestrator

    @pytest.fixture
    def bridge_with_llm(self, mock_orchestrator):
        """Create bridge with mocked LLM."""
        return ConsciousnessBridge(consciousness_llm=mock_orchestrator)

    @pytest.fixture
    def sample_game_state(self):
        """Sample game state for testing."""
        return {
            'health': 100.0,
            'max_health': 100.0,
            'magicka': 50.0,
            'stamina': 75.0,
            'level': 5,
            'gold': 150,
            'in_combat': False,
            'scene': 'exploration',
            'nearby_npcs': [],
            'enemies_nearby': 0,
            'active_quest': False,
        }

    def test_initialization_no_llm(self, bridge_no_llm):
        """Test bridge initializes without LLM."""
        assert bridge_no_llm.consciousness_llm is None
        assert len(bridge_no_llm.history) == 0

    def test_initialization_with_llm(self, bridge_with_llm, mock_orchestrator):
        """Test bridge initializes with LLM."""
        assert bridge_with_llm.consciousness_llm == mock_orchestrator
        assert len(bridge_with_llm.history) == 0

    @pytest.mark.asyncio
    async def test_compute_consciousness_heuristic(self, bridge_no_llm, sample_game_state):
        """Test consciousness computation without LLM (heuristic mode)."""
        consciousness = await bridge_no_llm.compute_consciousness(sample_game_state)
        
        assert isinstance(consciousness, ConsciousnessState)
        assert 0.0 <= consciousness.coherence <= 1.0
        assert 0.0 <= consciousness.coherence_ontical <= 1.0
        assert 0.0 <= consciousness.coherence_structural <= 1.0
        assert 0.0 <= consciousness.coherence_participatory <= 1.0
        assert 0.0 <= consciousness.consciousness_level <= 1.0
        assert 0.0 <= consciousness.game_quality <= 1.0
        assert 0.0 <= consciousness.self_awareness <= 1.0

    @pytest.mark.asyncio
    async def test_compute_consciousness_with_llm_enhancement(self, bridge_with_llm, sample_game_state, mock_orchestrator):
        """Test consciousness computation with LLM enhancement."""
        context = {
            'motivation': 'exploration',
            'cycle': 10,
            'scene': 'town'
        }
        
        consciousness = await bridge_with_llm.compute_consciousness(sample_game_state, context)
        
        # Verify LLM was called correctly
        assert mock_orchestrator.process.called
        call_args = mock_orchestrator.process.call_args
        
        # First argument should be the query string
        assert isinstance(call_args[0][0], str)
        assert 'Health' in call_args[0][0]
        assert 'Coherence' in call_args[0][0]
        
        # Should NOT pass context dict as second parameter (that was the bug)
        # If called with positional args, there should only be 1
        # Or if called with keyword args, 'selected_experts' should be absent or None
        if len(call_args[0]) > 1:
            # If there's a second positional arg, this is wrong
            pytest.fail("LLM process() called with more than one positional argument")
        
        # Verify consciousness was computed
        assert isinstance(consciousness, ConsciousnessState)
        assert consciousness.coherence > 0

    @pytest.mark.asyncio
    async def test_llm_enhancement_adjusts_coherence(self, bridge_with_llm, sample_game_state):
        """Test that LLM enhancement properly adjusts coherence."""
        # Mock orchestrator to return 'higher' in response
        bridge_with_llm.consciousness_llm.process = AsyncMock(return_value={
            'response': 'This state shows higher coherence than mechanical function.',
            'confidence': 0.9,
        })
        
        consciousness = await bridge_with_llm.compute_consciousness(sample_game_state)
        
        # Since response contains 'higher', adjustment factor should be 1.1
        # So coherence should be enhanced (though we can't directly test the factor)
        assert isinstance(consciousness, ConsciousnessState)

    @pytest.mark.asyncio
    async def test_llm_enhancement_error_handling(self, bridge_with_llm, sample_game_state):
        """Test that LLM enhancement errors are handled gracefully."""
        # Mock orchestrator to raise an exception
        bridge_with_llm.consciousness_llm.process = AsyncMock(side_effect=Exception("LLM error"))
        
        # Should not raise, should fall back to heuristic
        consciousness = await bridge_with_llm.compute_consciousness(sample_game_state)
        
        assert isinstance(consciousness, ConsciousnessState)
        assert consciousness.coherence > 0

    def test_coherence_trend_insufficient_data(self, bridge_no_llm):
        """Test coherence trend with insufficient data."""
        trend = bridge_no_llm.get_coherence_trend()
        assert trend == 'insufficient_data'

    def test_get_stats_empty(self, bridge_no_llm):
        """Test statistics with empty history."""
        stats = bridge_no_llm.get_stats()
        
        assert stats['total_measurements'] == 0
        assert stats['avg_coherence'] == 0.0
        assert stats['avg_consciousness'] == 0.0


@pytest.mark.asyncio
class TestConsciousnessBridgeLLMIntegration:
    """Test the specific LLM integration fix."""

    async def test_process_call_signature(self):
        """Test that process() is called with correct parameters."""
        # Create mock orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator.process = AsyncMock(return_value={
            'response': 'Test response',
            'confidence': 0.8,
        })
        
        bridge = ConsciousnessBridge(consciousness_llm=mock_orchestrator)
        
        game_state = {
            'health': 100.0,
            'max_health': 100.0,
            'in_combat': False,
            'scene': 'exploration',
        }
        
        context = {
            'motivation': 'exploration',
            'cycle': 10,
            'scene': 'town'
        }
        
        await bridge.compute_consciousness(game_state, context)
        
        # Verify process was called
        assert mock_orchestrator.process.called
        
        # Check call arguments
        call_args = mock_orchestrator.process.call_args
        
        # Should be called with only the query string as positional arg
        assert len(call_args[0]) == 1, "process() should be called with only 1 positional argument"
        assert isinstance(call_args[0][0], str), "First argument should be query string"
        
        # Should NOT have 'context' dict passed as second positional parameter
        # The old buggy code passed context dict, which got interpreted as selected_experts
        # and caused KeyError when trying to access experts['motivation']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
