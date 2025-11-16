"""
AGI Pattern Arbiter

Uses Singularis consciousness to interpret and enhance patterns
detected by rule-based pattern engine.

Architecture:
    Rule-Based Engine → Detects patterns (fast, deterministic)
    AGI Arbiter → Interprets patterns (smart, contextual)
"""

from __future__ import annotations

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from loguru import logger


@dataclass
class PatternInterpretation:
    """AGI's interpretation of a detected pattern."""
    
    # Original pattern info
    pattern_id: str
    pattern_name: str
    pattern_type: str  # 'habit', 'anomaly', 'correlation', 'trend'
    
    # AGI analysis
    significance: float  # 0-1: How important is this?
    confidence: float    # 0-1: How confident is AGI in interpretation?
    interpretation: str  # What does this pattern mean?
    insight: str         # Key insight or takeaway
    recommendation: Optional[str]  # What should user do?
    
    # Context
    contributing_factors: List[str]  # What causes this pattern?
    related_patterns: List[str]      # Other patterns that connect
    health_impact: Optional[str]     # Impact on health/wellbeing
    
    # Metadata
    timestamp: datetime
    arbiter_reasoning: str  # AGI's reasoning process
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        d = asdict(self)
        d['timestamp'] = self.timestamp.isoformat()
        return d


class AGIPatternArbiter:
    """
    AGI-powered pattern arbiter using Singularis consciousness.
    
    Takes patterns detected by rule-based engine and:
    1. Validates their significance
    2. Adds contextual interpretation
    3. Finds hidden connections
    4. Generates actionable insights
    """
    
    def __init__(self, consciousness):
        """
        Initialize arbiter.
        
        Args:
            consciousness: UnifiedConsciousnessLayer instance
        """
        self.consciousness = consciousness
        self.interpretation_cache: Dict[str, PatternInterpretation] = {}
        
        logger.info("[AGI-ARBITER] Pattern arbiter initialized")
    
    async def interpret_pattern(
        self,
        pattern: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> PatternInterpretation:
        """
        Interpret a single pattern using AGI.
        
        Args:
            pattern: Pattern dict from rule-based engine
            user_context: Additional user context
            
        Returns:
            PatternInterpretation with AGI insights
        """
        pattern_id = pattern.get('id', 'unknown')
        
        logger.info(f"[AGI-ARBITER] Interpreting pattern: {pattern.get('name', 'unnamed')}")
        
        # Build interpretation prompt
        prompt = self._build_interpretation_prompt(pattern, user_context)
        
        # Query consciousness (with life context automatically injected)
        response = await self.consciousness.process(
            query=prompt,
            subsystem_inputs={
                'pattern_data': pattern,
                'analysis_type': 'pattern_interpretation'
            },
            context=user_context or {}
        )
        
        # Parse AGI response
        interpretation = self._parse_interpretation_response(
            pattern,
            response.response,
            response.gpt5_analysis
        )
        
        # Cache for future reference
        self.interpretation_cache[pattern_id] = interpretation
        
        logger.info(
            f"[AGI-ARBITER] Pattern interpreted - "
            f"Significance: {interpretation.significance:.2f}, "
            f"Confidence: {interpretation.confidence:.2f}"
        )
        
        return interpretation
    
    async def interpret_patterns_batch(
        self,
        patterns: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[PatternInterpretation]:
        """
        Interpret multiple patterns in one AGI call (more efficient).
        
        Args:
            patterns: List of pattern dicts
            user_context: Additional user context
            
        Returns:
            List of PatternInterpretations
        """
        if not patterns:
            return []
        
        logger.info(f"[AGI-ARBITER] Batch interpreting {len(patterns)} patterns")
        
        # Build batch prompt
        prompt = self._build_batch_interpretation_prompt(patterns, user_context)
        
        # Single AGI call for all patterns
        response = await self.consciousness.process(
            query=prompt,
            subsystem_inputs={
                'patterns_data': patterns,
                'analysis_type': 'batch_pattern_interpretation'
            },
            context=user_context or {}
        )
        
        # Parse batch response
        interpretations = self._parse_batch_response(patterns, response.response)
        
        # Cache all
        for interp in interpretations:
            self.interpretation_cache[interp.pattern_id] = interp
        
        logger.info(f"[AGI-ARBITER] Batch interpretation complete")
        
        return interpretations
    
    async def find_hidden_correlations(
        self,
        patterns: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Use AGI to find correlations between patterns that rules missed.
        
        Args:
            patterns: List of detected patterns
            user_context: User context
            
        Returns:
            List of discovered correlations
        """
        logger.info(f"[AGI-ARBITER] Searching for hidden correlations in {len(patterns)} patterns")
        
        prompt = f"""
        Analyze these detected patterns and find hidden correlations:
        
        {json.dumps(patterns, indent=2)}
        
        Look for:
        1. Causal relationships (A causes B)
        2. Temporal correlations (A happens before B)
        3. Inverse relationships (more A = less B)
        4. Synergistic effects (A + B = enhanced outcome)
        
        Return JSON array of correlations:
        [
            {{
                "pattern1": "pattern_name",
                "pattern2": "pattern_name",
                "relationship": "causal|temporal|inverse|synergistic",
                "strength": 0.0-1.0,
                "explanation": "why these are correlated",
                "evidence": "what data supports this",
                "actionable_insight": "what user should do"
            }}
        ]
        """
        
        response = await self.consciousness.process(
            query=prompt,
            subsystem_inputs={'analysis_type': 'correlation_discovery'},
            context=user_context or {}
        )
        
        # Parse correlations
        try:
            correlations = json.loads(response.response)
            logger.info(f"[AGI-ARBITER] Found {len(correlations)} hidden correlations")
            return correlations
        except json.JSONDecodeError:
            logger.warning("[AGI-ARBITER] Failed to parse correlations, returning empty")
            return []
    
    def _build_interpretation_prompt(
        self,
        pattern: Dict[str, Any],
        user_context: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for single pattern interpretation."""
        
        prompt = f"""
        Interpret this behavioral pattern detected in user's life data:
        
        Pattern Details:
        - Name: {pattern.get('name', 'Unknown')}
        - Type: {pattern.get('type', 'Unknown')}
        - Description: {pattern.get('description', 'No description')}
        - Confidence: {pattern.get('confidence', 0):.2f}
        - Evidence: {pattern.get('evidence', 'None')}
        - Frequency: {pattern.get('frequency', 'Unknown')}
        
        Your task as an expert life coach and health analyst:
        
        1. **Assess Significance** (0-1): How important is this pattern?
           - Consider health impact, behavior change potential, urgency
        
        2. **Provide Interpretation**: What does this pattern mean?
           - Why is it happening?
           - What does it reveal about the user's life?
        
        3. **Generate Insight**: Key takeaway in one sentence
        
        4. **Recommend Action** (if applicable): What should user do?
           - Be specific and actionable
           - Consider user's context and capabilities
        
        5. **Identify Contributing Factors**: What causes this pattern?
        
        6. **Assess Health Impact**: How does this affect wellbeing?
        
        Respond in JSON format:
        {{
            "significance": 0.0-1.0,
            "confidence": 0.0-1.0,
            "interpretation": "detailed interpretation",
            "insight": "one-sentence key insight",
            "recommendation": "actionable recommendation or null",
            "contributing_factors": ["factor1", "factor2"],
            "health_impact": "positive|negative|neutral|mixed - explanation",
            "reasoning": "your reasoning process"
        }}
        """
        
        return prompt
    
    def _build_batch_interpretation_prompt(
        self,
        patterns: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for batch pattern interpretation."""
        
        patterns_summary = []
        for i, pattern in enumerate(patterns, 1):
            patterns_summary.append(
                f"{i}. {pattern.get('name', 'Unknown')} "
                f"({pattern.get('type', 'unknown')}): "
                f"{pattern.get('description', 'No description')}"
            )
        
        prompt = f"""
        Interpret these {len(patterns)} behavioral patterns detected in user's life data:
        
        {chr(10).join(patterns_summary)}
        
        For each pattern, provide:
        1. Significance score (0-1)
        2. Brief interpretation
        3. Key insight
        4. Recommendation (if needed)
        5. Health impact assessment
        
        Also identify:
        - Which patterns are most important (prioritize)
        - Any connections between patterns
        - Overall assessment of user's behavioral health
        
        Respond in JSON format:
        {{
            "patterns": [
                {{
                    "pattern_id": "pattern name",
                    "significance": 0.0-1.0,
                    "confidence": 0.0-1.0,
                    "interpretation": "brief interpretation",
                    "insight": "key insight",
                    "recommendation": "action or null",
                    "health_impact": "assessment"
                }}
            ],
            "priority_patterns": ["pattern1", "pattern2"],
            "pattern_connections": ["connection1", "connection2"],
            "overall_assessment": "overall behavioral health assessment"
        }}
        """
        
        return prompt
    
    def _parse_interpretation_response(
        self,
        pattern: Dict[str, Any],
        response: str,
        reasoning: str
    ) -> PatternInterpretation:
        """Parse AGI response into PatternInterpretation."""
        
        try:
            # Try to parse JSON response
            data = json.loads(response)
            
            return PatternInterpretation(
                pattern_id=pattern.get('id', 'unknown'),
                pattern_name=pattern.get('name', 'Unknown'),
                pattern_type=pattern.get('type', 'unknown'),
                significance=float(data.get('significance', 0.5)),
                confidence=float(data.get('confidence', 0.7)),
                interpretation=data.get('interpretation', response[:200]),
                insight=data.get('insight', 'Pattern detected'),
                recommendation=data.get('recommendation'),
                contributing_factors=data.get('contributing_factors', []),
                related_patterns=[],
                health_impact=data.get('health_impact'),
                timestamp=datetime.now(),
                arbiter_reasoning=data.get('reasoning', reasoning)
            )
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"[AGI-ARBITER] Failed to parse JSON, using fallback: {e}")
            
            # Fallback: Create interpretation from raw response
            return PatternInterpretation(
                pattern_id=pattern.get('id', 'unknown'),
                pattern_name=pattern.get('name', 'Unknown'),
                pattern_type=pattern.get('type', 'unknown'),
                significance=0.5,
                confidence=0.6,
                interpretation=response[:300],
                insight=response[:100],
                recommendation=None,
                contributing_factors=[],
                related_patterns=[],
                health_impact=None,
                timestamp=datetime.now(),
                arbiter_reasoning=reasoning
            )
    
    def _parse_batch_response(
        self,
        patterns: List[Dict[str, Any]],
        response: str
    ) -> List[PatternInterpretation]:
        """Parse batch AGI response."""
        
        try:
            data = json.loads(response)
            pattern_data = data.get('patterns', [])
            
            interpretations = []
            
            for i, pattern in enumerate(patterns):
                if i < len(pattern_data):
                    interp_data = pattern_data[i]
                    
                    interpretations.append(PatternInterpretation(
                        pattern_id=pattern.get('id', f'pattern_{i}'),
                        pattern_name=pattern.get('name', 'Unknown'),
                        pattern_type=pattern.get('type', 'unknown'),
                        significance=float(interp_data.get('significance', 0.5)),
                        confidence=float(interp_data.get('confidence', 0.7)),
                        interpretation=interp_data.get('interpretation', ''),
                        insight=interp_data.get('insight', ''),
                        recommendation=interp_data.get('recommendation'),
                        contributing_factors=[],
                        related_patterns=[],
                        health_impact=interp_data.get('health_impact'),
                        timestamp=datetime.now(),
                        arbiter_reasoning=data.get('overall_assessment', '')
                    ))
            
            return interpretations
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"[AGI-ARBITER] Failed to parse batch response: {e}")
            
            # Fallback: Create basic interpretations
            return [
                PatternInterpretation(
                    pattern_id=p.get('id', f'pattern_{i}'),
                    pattern_name=p.get('name', 'Unknown'),
                    pattern_type=p.get('type', 'unknown'),
                    significance=0.5,
                    confidence=0.6,
                    interpretation=p.get('description', ''),
                    insight='Pattern detected',
                    recommendation=None,
                    contributing_factors=[],
                    related_patterns=[],
                    health_impact=None,
                    timestamp=datetime.now(),
                    arbiter_reasoning='Fallback interpretation'
                )
                for i, p in enumerate(patterns)
            ]
    
    def get_cached_interpretation(self, pattern_id: str) -> Optional[PatternInterpretation]:
        """Get cached interpretation if available."""
        return self.interpretation_cache.get(pattern_id)
    
    def clear_cache(self):
        """Clear interpretation cache."""
        self.interpretation_cache.clear()
        logger.info("[AGI-ARBITER] Cache cleared")
