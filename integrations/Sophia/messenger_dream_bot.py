"""
Messenger Dream Bot - Integrates with Meta Glasses API for dream dictation.

Sends prompts via Messenger when user wakes up and records voice-dictated dreams.
Works with the existing meta-glasses-api browser extension.
"""

from typing import Optional, Callable
from datetime import datetime
import asyncio
import json


class MessengerDreamBot:
    """
    Messenger bot for dream recording via Meta Glasses.
    
    Integrates with the meta-glasses-api browser extension to:
    - Send wake-up prompts via Messenger
    - Receive voice-dictated dream transcriptions
    - Forward dreams to DreamAnalyst for analysis
    
    Setup:
    1. Meta Glasses API extension must be running
    2. Create a Messenger group chat named "Dream Journal"
    3. Set up monitoring in the extension
    4. Bot will send prompts and receive responses
    """
    
    def __init__(self, chat_name: str = "Dream Journal"):
        """
        Initialize Messenger Dream Bot.
        
        Args:
            chat_name: Name of the Messenger chat for dream recording
        """
        self.chat_name = chat_name
        self.dream_callback: Optional[Callable] = None
        self.pending_prompt = False
        self.last_prompt_time: Optional[datetime] = None
    
    def set_dream_callback(self, callback: Callable[[str, datetime], None]):
        """
        Set callback function for when dream is received.
        
        Args:
            callback: Function that takes (transcription, timestamp)
        """
        self.dream_callback = callback
    
    async def send_wake_prompt(self, wake_time: datetime, sleep_data: Optional[dict] = None):
        """
        Send prompt to user via Messenger to record their dream.
        
        This creates a message that will be sent through the meta-glasses-api
        extension to the user's Messenger chat.
        
        Args:
            wake_time: When user woke up
            sleep_data: Optional sleep quality data from Fitbit
        """
        # Generate personalized prompt
        prompt = self._generate_prompt(wake_time, sleep_data)
        
        # In production, this would interface with the meta-glasses-api
        # For now, we'll simulate the message structure
        message = {
            'type': 'dream_prompt',
            'chat': self.chat_name,
            'content': prompt,
            'timestamp': datetime.now().isoformat(),
            'wake_time': wake_time.isoformat()
        }
        
        print(f"\n📱 Sending dream prompt to Messenger chat '{self.chat_name}':")
        print(f"   {prompt}\n")
        
        # Mark that we're waiting for response
        self.pending_prompt = True
        self.last_prompt_time = datetime.now()
        
        # In production, send via meta-glasses-api websocket or API
        # await self._send_to_messenger(message)
        
        return message
    
    def _generate_prompt(self, wake_time: datetime, sleep_data: Optional[dict] = None) -> str:
        """Generate personalized wake-up prompt."""
        hour = wake_time.hour
        
        # Time-appropriate greeting
        if hour < 6:
            greeting = "Early riser! 🌅"
        elif hour < 10:
            greeting = "Good morning! ☀️"
        elif hour < 12:
            greeting = "Late morning! 🌤️"
        else:
            greeting = "Good afternoon! 🌞"
        
        prompt = f"{greeting}\n\n"
        prompt += "🌙 **Dream Journal Time** 🌙\n\n"
        
        # Add sleep quality context if available
        if sleep_data:
            quality = sleep_data.get('quality', 0)
            rem_minutes = sleep_data.get('rem_minutes', 0)
            
            if quality >= 80:
                prompt += f"You had excellent sleep (quality: {quality}/100)! "
            elif quality >= 60:
                prompt += f"You had good sleep (quality: {quality}/100). "
            else:
                prompt += f"Your sleep was okay (quality: {quality}/100). "
            
            if rem_minutes:
                prompt += f"You got {rem_minutes} minutes of REM sleep - great for dreaming!\n\n"
        
        prompt += "**Did you have any dreams?**\n\n"
        prompt += "If yes, please dictate your dream now. Include:\n"
        prompt += "• What happened in the dream\n"
        prompt += "• How you felt\n"
        prompt += "• Any notable symbols or characters\n"
        prompt += "• The setting/location\n\n"
        prompt += "Take your time and describe as much as you remember. "
        prompt += "I'll analyze it using Jungian and Freudian frameworks! 🧠✨\n\n"
        prompt += "Reply with your dream or 'no dream' if you don't remember."
        
        return prompt
    
    async def receive_dream_response(self, message: str, timestamp: datetime):
        """
        Receive dream dictation from user via Messenger.
        
        Args:
            message: User's voice-to-text dream transcription
            timestamp: When message was received
        """
        if not self.pending_prompt:
            print("⚠️ Received dream response but no prompt was pending")
            return
        
        # Check if user said they don't remember
        if any(phrase in message.lower() for phrase in ['no dream', "don't remember", "can't remember", 'nothing']):
            print("📝 User doesn't remember their dream")
            self.pending_prompt = False
            
            # Send acknowledgment
            response = "No worries! Not everyone remembers their dreams every day. "
            response += "Dream recall improves with practice. I'll check in tomorrow! 😊"
            print(f"📱 Sending: {response}")
            return
        
        # User provided a dream!
        print(f"\n✨ Dream received! ({len(message)} characters)")
        print(f"   Preview: {message[:100]}...")
        
        # Forward to dream analyst via callback
        if self.dream_callback:
            await self.dream_callback(message, timestamp)
        
        self.pending_prompt = False
        
        # Send acknowledgment
        response = "🌟 Thank you! I'm analyzing your dream now...\n\n"
        response += "I'll provide both Jungian and Freudian interpretations in a moment. "
        response += "This may reveal insights about your unconscious mind! 🧠"
        print(f"📱 Sending: {response}")
    
    async def send_analysis(self, analysis: dict):
        """
        Send dream analysis back to user via Messenger.
        
        Args:
            analysis: Dream analysis results from DreamAnalyst
        """
        # Format analysis for Messenger
        message = self._format_analysis(analysis)
        
        print(f"\n📱 Sending dream analysis to Messenger:")
        print(f"   {message[:200]}...\n")
        
        # In production, send via meta-glasses-api
        # await self._send_to_messenger({'content': message})
        
        return message
    
    def _format_analysis(self, analysis: dict) -> str:
        """Format analysis for Messenger display."""
        msg = "🔮 **Dream Analysis Complete** 🔮\n\n"
        
        # Jungian section
        msg += "**🌟 Jungian Interpretation**\n"
        msg += f"{analysis.get('jungian_interpretation', 'N/A')}\n\n"
        
        if analysis.get('identified_archetypes'):
            msg += "**Archetypes Identified:**\n"
            for archetype, explanation in analysis['identified_archetypes'][:3]:
                msg += f"• {archetype.value.replace('_', ' ').title()}: {explanation[:80]}...\n"
            msg += "\n"
        
        # Freudian section
        msg += "**🧠 Freudian Interpretation**\n"
        msg += f"{analysis.get('freudian_interpretation', 'N/A')}\n\n"
        
        if analysis.get('latent_content'):
            msg += f"**Hidden Meaning:** {analysis['latent_content'][:150]}...\n\n"
        
        # Synthesis
        if analysis.get('synthesis'):
            msg += "**💡 Integrated Insights**\n"
            msg += f"{analysis['synthesis'][:200]}...\n\n"
        
        # Recommendations
        if analysis.get('recommendations'):
            msg += "**📋 Recommendations:**\n"
            for rec in analysis['recommendations'][:3]:
                msg += f"• {rec}\n"
            msg += "\n"
        
        msg += f"Confidence: {analysis.get('confidence_score', 0) * 100:.0f}%\n\n"
        msg += "Sweet dreams tonight! 🌙✨"
        
        return msg
    
    def get_prompt_templates(self) -> dict:
        """Get various prompt templates for different scenarios."""
        return {
            'morning_prompt': (
                "Good morning! ☀️\n\n"
                "Did you have any dreams last night? "
                "If so, please tell me about them while they're still fresh in your memory!"
            ),
            'no_recall_encouragement': (
                "No worries! Dream recall improves with practice. Try these tips:\n"
                "• Keep a dream journal by your bed\n"
                "• Set intention before sleep: 'I will remember my dreams'\n"
                "• Don't move immediately upon waking\n"
                "• Write down even fragments\n\n"
                "See you tomorrow! 😊"
            ),
            'recurring_dream_prompt': (
                "I notice you've had similar dreams before. "
                "Recurring dreams often indicate unresolved psychological issues. "
                "Would you like to explore this pattern further?"
            ),
            'nightmare_support': (
                "That sounds like a difficult dream. Nightmares can be distressing, "
                "but they're your mind's way of processing fears and anxieties. "
                "Would you like some techniques for managing nightmares?"
            ),
            'lucid_dream_congratulations': (
                "Wow, a lucid dream! That's when you become aware you're dreaming. "
                "This is a powerful state for self-exploration. "
                "With practice, you can even control your dreams! 🌟"
            )
        }
    
    async def send_weekly_summary(self, summary: dict):
        """Send weekly dream pattern summary."""
        msg = "📊 **Weekly Dream Summary** 📊\n\n"
        msg += f"Dreams recorded: {summary.get('total_dreams', 0)}\n"
        msg += f"Most common theme: {summary.get('top_theme', 'N/A')}\n"
        msg += f"Most common symbol: {summary.get('top_symbol', 'N/A')}\n\n"
        
        if summary.get('patterns'):
            msg += "**Recurring Patterns:**\n"
            for pattern in summary['patterns'][:3]:
                msg += f"• {pattern}\n"
            msg += "\n"
        
        if summary.get('insights'):
            msg += f"**Key Insight:** {summary['insights']}\n\n"
        
        msg += "Keep up the great dream journaling! 🌙✨"
        
        print(f"\n📱 Sending weekly summary:\n{msg}")
        return msg


# Integration with meta-glasses-api
class MetaGlassesAPIBridge:
    """
    Bridge to communicate with meta-glasses-api browser extension.
    
    The meta-glasses-api extension monitors Messenger and can send/receive messages.
    This class provides the interface to trigger dream prompts and receive responses.
    """
    
    def __init__(self, extension_port: int = 8080):
        """
        Initialize bridge to meta-glasses-api.
        
        Args:
            extension_port: Port where extension API is listening
        """
        self.extension_port = extension_port
        self.base_url = f"http://localhost:{extension_port}"
    
    async def send_message(self, chat_name: str, message: str):
        """
        Send message to Messenger chat via extension.
        
        Args:
            chat_name: Name of the chat (e.g., "Dream Journal")
            message: Message content to send
        """
        # This would interface with the actual meta-glasses-api
        # For now, it's a placeholder showing the intended structure
        payload = {
            'action': 'send_message',
            'chat': chat_name,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"📤 Sending to meta-glasses-api: {chat_name}")
        # In production: await aiohttp.post(f"{self.base_url}/send", json=payload)
    
    async def register_webhook(self, callback_url: str):
        """
        Register webhook to receive messages from extension.
        
        Args:
            callback_url: URL where dream bot will receive messages
        """
        payload = {
            'action': 'register_webhook',
            'url': callback_url,
            'events': ['message_received']
        }
        
        print(f"🔗 Registering webhook: {callback_url}")
        # In production: await aiohttp.post(f"{self.base_url}/webhook", json=payload)


if __name__ == "__main__":
    # Demo usage
    print("=== MESSENGER DREAM BOT DEMO ===\n")
    
    # Initialize bot
    bot = MessengerDreamBot(chat_name="Dream Journal")
    
    # Simulate wake-up
    wake_time = datetime.now()
    sleep_data = {
        'quality': 75,
        'rem_minutes': 95,
        'duration_hours': 7.5
    }
    
    # Send prompt
    print("Simulating wake-up prompt...")
    asyncio.run(bot.send_wake_prompt(wake_time, sleep_data))
    
    # Simulate user response
    print("\nSimulating user dream dictation...")
    dream_text = (
        "I was in a dark forest and there was a snake following me. "
        "I felt really anxious and scared. Then I found a bridge over water "
        "and when I crossed it I felt peaceful. There was an old man on the other side "
        "who smiled at me and I woke up feeling calm."
    )
    
    asyncio.run(bot.receive_dream_response(dream_text, datetime.now()))
    
    # Simulate analysis result
    print("\nSimulating analysis delivery...")
    analysis = {
        'jungian_interpretation': "Forest represents the unconscious, snake is transformation...",
        'identified_archetypes': [
            ('shadow', 'The snake represents your shadow self'),
            ('wise_old_man', 'The old man represents inner wisdom')
        ],
        'freudian_interpretation': "Anxiety suggests repressed content...",
        'latent_content': "The dream processes fear of change and desire for guidance",
        'synthesis': "Both frameworks reveal a journey from fear to acceptance",
        'recommendations': [
            "Explore what changes you're resisting",
            "Seek guidance from mentors",
            "Practice shadow integration"
        ],
        'confidence_score': 0.85
    }
    
    asyncio.run(bot.send_analysis(analysis))
    
    print("\n✅ Demo complete!")
    print("\n💡 Setup Instructions:")
    print("1. Ensure meta-glasses-api extension is running")
    print("2. Create Messenger group chat named 'Dream Journal'")
    print("3. Start monitoring the chat in the extension")
    print("4. Connect Fitbit for automatic wake detection")
    print("5. System will automatically prompt you each morning!")
