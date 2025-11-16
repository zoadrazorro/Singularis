"""
Dream Analysis System - Complete Demo

Demonstrates the full workflow from wake detection to dream analysis.
"""

import asyncio
from datetime import datetime, time
from dream_analyst import DreamAnalyst, EmotionalTone, DreamType
from fitbit_integration import FitbitIntegration, SleepData
from messenger_dream_bot import MessengerDreamBot


async def demo_complete_workflow():
    """Demonstrate complete dream analysis workflow."""
    
    print("=" * 80)
    print("  DREAM ANALYSIS SYSTEM - Complete Workflow Demo")
    print("=" * 80)
    
    # Initialize components
    print("\n🔧 Initializing components...")
    analyst = DreamAnalyst()
    messenger = MessengerDreamBot("Dream Journal")
    
    print("   ✓ Dream Analyst initialized")
    print("   ✓ Messenger Bot initialized")
    
    # Simulate wake-up detection
    print("\n" + "=" * 80)
    print("  STEP 1: WAKE-UP DETECTED (Fitbit)")
    print("=" * 80)
    
    wake_time = datetime.now().replace(hour=7, minute=30, second=0)
    sleep_data = {
        'quality': 82,
        'rem_minutes': 95,
        'duration_hours': 7.5,
        'deep_minutes': 65,
        'light_minutes': 180
    }
    
    print(f"\n☀️ User woke up at {wake_time.strftime('%H:%M')}")
    print(f"   Sleep quality: {sleep_data['quality']}/100")
    print(f"   REM sleep: {sleep_data['rem_minutes']} minutes")
    print(f"   Deep sleep: {sleep_data['deep_minutes']} minutes")
    print(f"   Total duration: {sleep_data['duration_hours']} hours")
    
    # Send prompt
    print("\n" + "=" * 80)
    print("  STEP 2: SEND PROMPT (Messenger Bot)")
    print("=" * 80)
    
    await messenger.send_wake_prompt(wake_time, sleep_data)
    
    # Simulate user response
    print("\n" + "=" * 80)
    print("  STEP 3: USER DICTATES DREAM (Voice)")
    print("=" * 80)
    
    dream_transcription = """
    I was walking through a dark forest at night. The trees were really tall and I felt 
    anxious because I couldn't see the path. Then I saw a snake on the ground and it 
    started following me. I was really scared and started running. 
    
    Eventually I came to a bridge over water. The water was calm and reflected the moonlight. 
    When I crossed the bridge I felt peaceful and the anxiety went away. 
    
    On the other side there was an old man with a white beard sitting by a fire. He smiled 
    at me and gestured for me to sit down. I felt safe and calm. Then I woke up.
    """
    
    print("\n📱 User dictates dream via Messenger:")
    print(f"   Length: {len(dream_transcription)} characters")
    print(f"   Preview: {dream_transcription[:150].strip()}...")
    
    # Record dream
    print("\n" + "=" * 80)
    print("  STEP 4: RECORD & PROCESS DREAM")
    print("=" * 80)
    
    dream = analyst.record_dream(
        transcription=dream_transcription,
        wake_time=wake_time,
        sleep_data=sleep_data
    )
    
    print(f"\n✅ Dream recorded: {dream.id}")
    print(f"   Date: {dream.date}")
    print(f"   Emotional tone: {dream.emotional_tone.value}")
    print(f"   Dream type: {dream.dream_type.value}")
    print(f"   Symbols found: {len(dream.symbols)}")
    if dream.symbols:
        print(f"   Symbols: {', '.join(s.symbol for s in dream.symbols)}")
    print(f"   Themes: {', '.join(dream.themes) if dream.themes else 'None'}")
    
    # Analyze dream
    print("\n" + "=" * 80)
    print("  STEP 5: ANALYZE DREAM (Jungian + Freudian)")
    print("=" * 80)
    
    print("\n🔮 Analyzing dream...")
    analysis = analyst.analyze_dream(dream.id)
    
    print(f"\n✅ Analysis complete!")
    print(f"   Confidence: {analysis.confidence_score * 100:.0f}%")
    print(f"   Archetypes identified: {len(analysis.identified_archetypes)}")
    print(f"   Mechanisms identified: {len(analysis.identified_mechanisms)}")
    
    # Display analysis
    print("\n" + "=" * 80)
    print("  JUNGIAN INTERPRETATION")
    print("=" * 80)
    
    print(f"\n{analysis.jungian_interpretation}")
    
    if analysis.identified_archetypes:
        print("\n**Archetypes:**")
        for archetype, explanation in analysis.identified_archetypes:
            print(f"  • {archetype.value.replace('_', ' ').title()}: {explanation}")
    
    print("\n" + "=" * 80)
    print("  FREUDIAN INTERPRETATION")
    print("=" * 80)
    
    print(f"\n{analysis.freudian_interpretation}")
    
    if analysis.latent_content:
        print(f"\n**Latent Content (Hidden Meaning):**")
        print(f"  {analysis.latent_content}")
    
    print("\n" + "=" * 80)
    print("  INTEGRATED SYNTHESIS")
    print("=" * 80)
    
    print(f"\n{analysis.synthesis}")
    
    # Recommendations
    print("\n" + "=" * 80)
    print("  RECOMMENDATIONS")
    print("=" * 80)
    
    if analysis.recommendations:
        print()
        for i, rec in enumerate(analysis.recommendations, 1):
            print(f"  {i}. {rec}")
    
    # Send analysis to user
    print("\n" + "=" * 80)
    print("  STEP 6: SEND ANALYSIS TO USER (Messenger)")
    print("=" * 80)
    
    analysis_dict = {
        'jungian_interpretation': analysis.jungian_interpretation,
        'identified_archetypes': analysis.identified_archetypes,
        'freudian_interpretation': analysis.freudian_interpretation,
        'latent_content': analysis.latent_content,
        'identified_mechanisms': analysis.identified_mechanisms,
        'synthesis': analysis.synthesis,
        'recommendations': analysis.recommendations,
        'confidence_score': analysis.confidence_score
    }
    
    await messenger.send_analysis(analysis_dict)
    
    # Show statistics
    print("\n" + "=" * 80)
    print("  DREAM STATISTICS")
    print("=" * 80)
    
    # Add a few more dreams for demo
    print("\n📊 Adding sample dreams for pattern analysis...")
    
    # Dream 2
    analyst.record_dream(
        "I was flying over mountains and felt free and happy",
        datetime.now().replace(hour=7, minute=0),
        {'quality': 75, 'rem_minutes': 85}
    )
    
    # Dream 3
    analyst.record_dream(
        "I was in a house with many rooms and got lost. There was water everywhere",
        datetime.now().replace(hour=6, minute=45),
        {'quality': 68, 'rem_minutes': 70}
    )
    
    # Dream 4
    analyst.record_dream(
        "A snake appeared in my garden and I wasn't afraid. It transformed into a bird",
        datetime.now().replace(hour=7, minute=15),
        {'quality': 80, 'rem_minutes': 90}
    )
    
    report = analyst.get_dream_report(days=30)
    
    print(f"\n✅ Total dreams recorded: {report['total_dreams']}")
    
    if report['most_common_themes']:
        print(f"\n**Most Common Themes:**")
        for theme, count in report['most_common_themes']:
            print(f"  • {theme}: {count} times")
    
    if report['most_common_symbols']:
        print(f"\n**Most Common Symbols:**")
        for symbol, count in report['most_common_symbols']:
            print(f"  • {symbol}: {count} times")
    
    if report.get('recommendations'):
        print(f"\n**Pattern-Based Recommendations:**")
        for rec in report['recommendations']:
            print(f"  • {rec}")
    
    # Final summary
    print("\n" + "=" * 80)
    print("  WORKFLOW COMPLETE ✨")
    print("=" * 80)
    
    print("\n✅ System successfully:")
    print("   1. Detected wake-up (Fitbit)")
    print("   2. Sent personalized prompt (Messenger)")
    print("   3. Received voice dictation")
    print("   4. Recorded and processed dream")
    print("   5. Analyzed with Jungian + Freudian frameworks")
    print("   6. Sent interpretation to user")
    print("   7. Tracked patterns over time")
    
    print("\n💡 In production, this runs automatically every morning!")
    print("   Just wake up, check Messenger, and dictate your dreams.")
    
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(demo_complete_workflow())
