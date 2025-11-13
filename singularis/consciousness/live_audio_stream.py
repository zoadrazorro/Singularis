"""
Live Audio Stream System

Real-time audio commentary from Gemini 2.5 Flash Live and OpenAI GPT-4 Realtime
for continuous AGI thought vocalization during gameplay.
"""

import asyncio
import time
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass
from enum import Enum
import queue
import threading
from loguru import logger

try:
    import pygame_ce as pygame
except ImportError:
    try:
        import pygame
    except ImportError:
        pygame = None
        logger.warning("pygame not available - audio playback disabled")


class StreamProvider(Enum):
    """Audio stream provider."""
    GEMINI_FLASH_LIVE = "gemini-2.5-flash-live"
    OPENAI_REALTIME = "gpt-4-realtime"
    GEMINI_TTS = "gemini-2.5-pro-tts"


class StreamPriority(Enum):
    """Stream priority levels."""
    CRITICAL = 4  # Immediate threats, errors
    HIGH = 3      # Important decisions, discoveries
    MEDIUM = 2    # Observations, analysis
    LOW = 1       # Background thoughts, musings
    AMBIENT = 0   # Continuous narration


@dataclass
class AudioStreamConfig:
    """Configuration for live audio streaming."""
    
    # Providers
    enable_gemini_live: bool = True
    enable_openai_realtime: bool = True
    enable_gemini_tts: bool = False  # Fallback TTS
    
    # Stream settings
    stream_frequency: float = 5.0  # Seconds between stream updates
    min_priority: StreamPriority = StreamPriority.MEDIUM
    max_concurrent_streams: int = 2  # Max simultaneous audio streams
    
    # Audio settings
    volume: float = 0.8
    audio_format: str = "mp3"  # or "wav", "ogg"
    sample_rate: int = 24000
    
    # Content settings
    narration_style: str = "analytical"  # analytical, dramatic, technical, casual
    include_reasoning: bool = True  # Include thought process
    include_emotions: bool = True   # Include affective state
    include_metrics: bool = False   # Include performance metrics
    
    # Rate limiting
    max_streams_per_minute: int = 12  # Prevent spam


class LiveAudioStream:
    """
    Live audio streaming system for real-time AGI commentary.
    
    Provides continuous audio narration of AGI thoughts, decisions, and observations
    using Gemini 2.5 Flash Live and OpenAI GPT-4 Realtime APIs.
    """
    
    def __init__(self, config: AudioStreamConfig):
        self.config = config
        self.running = False
        
        # Audio queue
        self.audio_queue = asyncio.Queue(maxsize=10)
        self.playback_queue = queue.Queue(maxsize=5)
        
        # Stream state
        self.active_streams: List[str] = []
        self.stream_history: List[Dict[str, Any]] = []
        self.last_stream_time = 0
        self.streams_this_minute = 0
        self.minute_reset_time = time.time()
        
        # Pygame mixer for audio playback
        if pygame:
            try:
                pygame.mixer.init(frequency=config.sample_rate, channels=1)
                pygame.mixer.set_num_channels(config.max_concurrent_streams)
                logger.info("Audio mixer initialized")
            except Exception as e:
                logger.error(f"Failed to initialize audio mixer: {e}")
                pygame = None
        
        # API clients (initialized later)
        self.gemini_client = None
        self.openai_client = None
        
        # Callbacks
        self.on_stream_start: Optional[Callable] = None
        self.on_stream_complete: Optional[Callable] = None
        self.on_audio_chunk: Optional[Callable] = None
        
        # Statistics
        self.stats = {
            'total_streams': 0,
            'gemini_streams': 0,
            'openai_streams': 0,
            'gemini_tts_streams': 0,
            'total_duration': 0.0,
            'avg_latency': 0.0,
            'errors': 0,
            'primary_failures': 0,
            'fallback_successes': 0,
            'total_failures': 0,
        }
    
    async def initialize(self):
        """Initialize API clients."""
        if self.config.enable_gemini_live:
            try:
                import google.generativeai as genai
                self.gemini_client = genai
                logger.info("Gemini Flash Live client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
        
        if self.config.enable_openai_realtime:
            try:
                import openai
                self.openai_client = openai.AsyncOpenAI()
                logger.info("OpenAI Realtime client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
    
    async def start(self):
        """Start the audio streaming system."""
        if self.running:
            return
        
        self.running = True
        logger.info("🎙️ Live audio stream started")
        
        # Start background tasks
        asyncio.create_task(self._stream_processor())
        asyncio.create_task(self._audio_player())
        asyncio.create_task(self._rate_limit_resetter())
    
    async def stop(self):
        """Stop the audio streaming system."""
        self.running = False
        logger.info("🎙️ Live audio stream stopped")
        
        # Clear queues
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except:
                break
    
    async def stream_thought(
        self,
        context: Dict[str, Any],
        priority: StreamPriority = StreamPriority.MEDIUM,
        provider: Optional[StreamProvider] = None
    ) -> Optional[str]:
        """
        Stream a thought/observation as audio.
        
        Args:
            context: Context dict with perception, action, reasoning, etc.
            priority: Stream priority level
            provider: Preferred provider (auto-select if None)
            
        Returns:
            Stream ID if queued, None if rejected
        """
        # Check priority threshold
        if priority.value < self.config.min_priority.value:
            return None
        
        # Check rate limiting
        if not self._check_rate_limit():
            logger.warning("Rate limit exceeded, skipping stream")
            return None
        
        # Auto-select provider
        if provider is None:
            provider = self._select_provider(priority)
        
        # Create stream request
        stream_id = f"stream_{int(time.time() * 1000)}"
        request = {
            'stream_id': stream_id,
            'context': context,
            'priority': priority,
            'provider': provider,
            'timestamp': time.time(),
        }
        
        # Queue for processing
        try:
            await self.audio_queue.put(request)
            logger.debug(f"Queued audio stream: {stream_id} ({provider.value})")
            return stream_id
        except asyncio.QueueFull:
            logger.warning("Audio queue full, dropping stream")
            return None
    
    async def stream_decision(
        self,
        action: str,
        reasoning: str,
        confidence: float,
        scene_type: str
    ):
        """Stream a decision announcement."""
        context = {
            'type': 'decision',
            'action': action,
            'reasoning': reasoning,
            'confidence': confidence,
            'scene': scene_type,
        }
        await self.stream_thought(context, StreamPriority.HIGH)
    
    async def stream_observation(
        self,
        observation: str,
        visual_analysis: str,
        importance: float
    ):
        """Stream an observation/perception."""
        priority = StreamPriority.HIGH if importance > 0.7 else StreamPriority.MEDIUM
        context = {
            'type': 'observation',
            'observation': observation,
            'visual': visual_analysis,
            'importance': importance,
        }
        await self.stream_thought(context, priority)
    
    async def stream_discovery(
        self,
        discovery: str,
        significance: float
    ):
        """Stream a discovery/insight."""
        context = {
            'type': 'discovery',
            'discovery': discovery,
            'significance': significance,
        }
        await self.stream_thought(context, StreamPriority.CRITICAL)
    
    async def stream_ambient(
        self,
        narration: str
    ):
        """Stream ambient narration."""
        context = {
            'type': 'ambient',
            'narration': narration,
        }
        await self.stream_thought(context, StreamPriority.AMBIENT)
    
    def _check_rate_limit(self) -> bool:
        """Check if rate limit allows new stream."""
        current_time = time.time()
        
        # Reset counter every minute
        if current_time - self.minute_reset_time >= 60:
            self.streams_this_minute = 0
            self.minute_reset_time = current_time
        
        # Check limit
        if self.streams_this_minute >= self.config.max_streams_per_minute:
            return False
        
        # Check minimum interval
        if current_time - self.last_stream_time < (60.0 / self.config.max_streams_per_minute):
            return False
        
        return True
    
    def _select_provider(self, priority: StreamPriority) -> StreamProvider:
        """Select best provider for priority level."""
        # Critical/High priority: Use OpenAI Realtime for lowest latency
        if priority.value >= StreamPriority.HIGH.value and self.config.enable_openai_realtime:
            return StreamProvider.OPENAI_REALTIME
        
        # Medium priority: Use Gemini Flash Live (unlimited)
        if self.config.enable_gemini_live:
            return StreamProvider.GEMINI_FLASH_LIVE
        
        # Fallback to TTS
        return StreamProvider.GEMINI_TTS
    
    async def _stream_processor(self):
        """Background task to process stream requests."""
        while self.running:
            try:
                # Get next request
                request = await asyncio.wait_for(
                    self.audio_queue.get(),
                    timeout=1.0
                )
                
                # Process stream
                await self._process_stream(request)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Stream processor error: {e}")
                self.stats['errors'] += 1
    
    async def _process_stream(self, request: Dict[str, Any]):
        """Process a single stream request."""
        stream_id = request['stream_id']
        provider = request['provider']
        context = request['context']
        
        logger.info(f"🎙️ Processing stream {stream_id} via {provider.value}")
        
        start_time = time.time()
        audio_data = None
        
        try:
            # Generate prompt
            prompt = self._generate_prompt(context)
            
            # Try primary provider with fallback chain
            if provider == StreamProvider.GEMINI_FLASH_LIVE:
                audio_data = await self._stream_with_fallback(
                    prompt,
                    primary=self._stream_gemini_live,
                    fallbacks=[
                        self._stream_openai_realtime,
                        self._stream_gemini_tts,
                    ]
                )
            elif provider == StreamProvider.OPENAI_REALTIME:
                audio_data = await self._stream_with_fallback(
                    prompt,
                    primary=self._stream_openai_realtime,
                    fallbacks=[
                        self._stream_gemini_live,
                        self._stream_gemini_tts,
                    ]
                )
            else:
                audio_data = await self._stream_gemini_tts(prompt)
            
            if audio_data:
                # Queue for playback
                self.playback_queue.put({
                    'stream_id': stream_id,
                    'audio': audio_data,
                    'timestamp': time.time(),
                })
                
                # Update stats (provider-specific stats tracked in _track_provider_success)
                duration = time.time() - start_time
                self.stats['total_streams'] += 1
                self.stats['total_duration'] += duration
                self.stats['avg_latency'] = self.stats['total_duration'] / self.stats['total_streams']
                
                # Update rate limiting
                self.last_stream_time = time.time()
                self.streams_this_minute += 1
                
                # Callback
                if self.on_stream_complete:
                    self.on_stream_complete(stream_id, duration)
                
                logger.info(f"✓ Stream {stream_id} completed in {duration:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to process stream {stream_id}: {e}")
            self.stats['errors'] += 1
    
    async def _stream_with_fallback(
        self,
        prompt: str,
        primary: Callable,
        fallbacks: List[Callable]
    ) -> Optional[bytes]:
        """
        Try primary stream provider, fall back to alternatives on failure.
        
        Args:
            prompt: Text prompt to stream
            primary: Primary streaming function
            fallbacks: List of fallback functions to try in order
            
        Returns:
            Audio bytes or None
        """
        # Try primary
        try:
            logger.debug(f"Trying primary provider: {primary.__name__}")
            audio_data = await primary(prompt)
            if audio_data:
                logger.info(f"✓ Primary provider succeeded: {primary.__name__}")
                self._track_provider_success(primary.__name__)
                return audio_data
            logger.warning(f"Primary provider returned no data: {primary.__name__}")
        except Exception as e:
            logger.warning(f"Primary provider failed: {primary.__name__} - {e}")
            self.stats['primary_failures'] += 1
        
        # Try fallbacks in order
        for i, fallback in enumerate(fallbacks, 1):
            try:
                logger.info(f"Trying fallback {i}/{len(fallbacks)}: {fallback.__name__}")
                audio_data = await fallback(prompt)
                if audio_data:
                    logger.info(f"✓ Fallback {i} succeeded: {fallback.__name__}")
                    self.stats['fallback_successes'] += 1
                    self._track_provider_success(fallback.__name__)
                    return audio_data
                logger.warning(f"Fallback {i} returned no data: {fallback.__name__}")
            except Exception as e:
                logger.warning(f"Fallback {i} failed: {fallback.__name__} - {e}")
                continue
        
        # All providers failed
        logger.error("All audio stream providers failed")
        self.stats['total_failures'] += 1
        return None
    
    def _track_provider_success(self, provider_name: str):
        """Track which provider succeeded."""
        if 'gemini_live' in provider_name.lower():
            self.stats['gemini_streams'] += 1
        elif 'openai' in provider_name.lower():
            self.stats['openai_streams'] += 1
        elif 'gemini_tts' in provider_name.lower():
            self.stats['gemini_tts_streams'] += 1
    
    def _generate_prompt(self, context: Dict[str, Any]) -> str:
        """Generate narration prompt from context."""
        ctx_type = context.get('type', 'unknown')
        style = self.config.narration_style
        
        if ctx_type == 'decision':
            prompt = f"As an AGI playing Skyrim, narrate this decision in a {style} style:\n"
            prompt += f"Action: {context['action']}\n"
            prompt += f"Reasoning: {context['reasoning']}\n"
            prompt += f"Confidence: {context['confidence']:.0%}\n"
            prompt += f"Scene: {context['scene']}\n"
            prompt += "\nProvide a brief, engaging narration (1-2 sentences)."
        
        elif ctx_type == 'observation':
            prompt = f"As an AGI, narrate this observation in a {style} style:\n"
            prompt += f"{context['observation']}\n"
            prompt += f"Visual analysis: {context['visual']}\n"
            prompt += "\nProvide a brief narration (1-2 sentences)."
        
        elif ctx_type == 'discovery':
            prompt = f"As an AGI, excitedly narrate this discovery:\n"
            prompt += f"{context['discovery']}\n"
            prompt += "\nExpress the significance in an engaging way (1-2 sentences)."
        
        elif ctx_type == 'ambient':
            prompt = f"As an AGI, provide ambient narration:\n"
            prompt += f"{context['narration']}\n"
        
        else:
            prompt = f"Narrate: {context}"
        
        return prompt
    
    async def _stream_gemini_live(self, prompt: str) -> Optional[bytes]:
        """Stream audio using Gemini 2.5 Flash Live."""
        if not self.gemini_client:
            return None
        
        try:
            # Use Gemini Flash Live for streaming
            model = self.gemini_client.GenerativeModel('gemini-2.5-flash-live')
            
            # Generate with audio output
            response = await asyncio.to_thread(
                model.generate_content,
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'max_output_tokens': 100,
                }
            )
            
            # Extract audio (implementation depends on API)
            # For now, return text for TTS conversion
            text = response.text
            
            # Convert to audio using TTS
            return await self._text_to_speech(text, "gemini")
            
        except Exception as e:
            logger.error(f"Gemini Live stream error: {e}")
            return None
    
    async def _stream_openai_realtime(self, prompt: str) -> Optional[bytes]:
        """Stream audio using OpenAI GPT-4 Realtime."""
        if not self.openai_client:
            return None
        
        try:
            # Use OpenAI Realtime API for audio streaming
            response = await self.openai_client.audio.speech.create(
                model="gpt-4-realtime",
                voice="nova",
                input=prompt,
                response_format="mp3",
            )
            
            return response.content
            
        except Exception as e:
            logger.error(f"OpenAI Realtime stream error: {e}")
            return None
    
    async def _stream_gemini_tts(self, prompt: str) -> Optional[bytes]:
        """Fallback TTS using Gemini."""
        try:
            # Generate text first
            model = self.gemini_client.GenerativeModel('gemini-2.5-flash-lite')
            response = await asyncio.to_thread(
                model.generate_content,
                prompt,
                generation_config={'max_output_tokens': 100}
            )
            
            text = response.text
            return await self._text_to_speech(text, "gemini")
            
        except Exception as e:
            logger.error(f"Gemini TTS error: {e}")
            return None
    
    async def _text_to_speech(self, text: str, provider: str) -> Optional[bytes]:
        """Convert text to speech."""
        # Placeholder - implement actual TTS
        logger.info(f"TTS ({provider}): {text}")
        return None
    
    async def _audio_player(self):
        """Background task to play audio."""
        while self.running:
            try:
                # Get next audio
                audio_data = await asyncio.to_thread(
                    self.playback_queue.get,
                    timeout=1.0
                )
                
                # Play audio
                if pygame and audio_data['audio']:
                    await self._play_audio(audio_data['audio'])
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Audio player error: {e}")
    
    async def _play_audio(self, audio_bytes: bytes):
        """Play audio bytes."""
        if not pygame:
            return
        
        try:
            # Save to temp file and play
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                f.write(audio_bytes)
                temp_path = f.name
            
            # Load and play
            sound = pygame.mixer.Sound(temp_path)
            sound.set_volume(self.config.volume)
            channel = sound.play()
            
            # Wait for completion
            while channel.get_busy():
                await asyncio.sleep(0.1)
            
            # Cleanup
            import os
            os.unlink(temp_path)
            
        except Exception as e:
            logger.error(f"Audio playback error: {e}")
    
    async def _rate_limit_resetter(self):
        """Reset rate limit counter every minute."""
        while self.running:
            await asyncio.sleep(60)
            self.streams_this_minute = 0
            logger.debug("Rate limit counter reset")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get streaming statistics."""
        return {
            **self.stats,
            'active_streams': len(self.active_streams),
            'queue_size': self.audio_queue.qsize(),
            'playback_queue_size': self.playback_queue.qsize(),
            'streams_this_minute': self.streams_this_minute,
        }
