"""Test enhanced symbolic logic system."""

from singularis.skyrim import SkyrimWorldModel

print("="*70)
print("Testing Enhanced Symbolic Logic System")
print("="*70)

wm = SkyrimWorldModel()

# Test 1: Dungeon combat scenario
print("\n1. DUNGEON COMBAT SCENARIO")
print("-" * 70)
test_state = {
    'health': 25,
    'in_combat': True,
    'enemies_nearby': 4,
    'location': 'Bleak Falls Barrow',
    'scene': 'indoor_dungeon',
    'stamina': 20,
    'magicka': 80,
    'bounty': 0
}

analysis = wm.get_logic_analysis(test_state)
print(f"Location: {test_state['location']}")
print(f"Health: {test_state['health']}, Stamina: {test_state['stamina']}, Magicka: {test_state['magicka']}")
print(f"Enemies: {test_state['enemies_nearby']}, In Combat: {test_state['in_combat']}")
print(f"\nLogic Confidence: {analysis['logic_confidence']:.2f}")
print(f"Active Facts: {len(analysis['current_facts'])}")
print(f"Applicable Rules: {len(analysis['applicable_rules'])}")
print(f"\nRecommendations:")
for reason in analysis['recommendations']['logical_reasoning']:
    print(f"  • {reason}")

# Test 2: Outdoor exploration scenario
print("\n2. OUTDOOR EXPLORATION SCENARIO")
print("-" * 70)
test_state2 = {
    'health': 85,
    'in_combat': False,
    'enemies_nearby': 0,
    'location': 'Whiterun Plains',
    'scene': 'outdoor_wilderness',
    'stamina': 90,
    'magicka': 95,
    'bounty': 0
}

analysis2 = wm.get_logic_analysis(test_state2)
print(f"Location: {test_state2['location']}")
print(f"Health: {test_state2['health']}, Stamina: {test_state2['stamina']}")
print(f"\nLogic Confidence: {analysis2['logic_confidence']:.2f}")
print(f"Active Facts: {len(analysis2['current_facts'])}")
print(f"Recommendations:")
for reason in analysis2['recommendations']['logical_reasoning']:
    print(f"  • {reason}")

# Test 3: Rule confidence adjustment
print("\n3. RULE CONFIDENCE ADJUSTMENT TEST")
print("-" * 70)

# Simulate using a recommendation
used_recommendations = ['should_heal']
print(f"Simulating outcome: Followed 'should_heal' recommendation")
print(f"Before adjustment:")
for rule in wm.logic_engine.rules:
    if 'ShouldHeal' in str(rule.conclusion):
        print(f"  {rule}")
        print(f"  Usage: {rule.usage_count}x, Success: {rule.success_count}x")

# Adjust based on success
wm.update_rule_confidences_from_outcome(used_recommendations, True, 1)

print(f"\nAfter successful outcome:")
for rule in wm.logic_engine.rules:
    if 'ShouldHeal' in str(rule.conclusion):
        print(f"  {rule}")
        print(f"  Usage: {rule.usage_count}x, Success: {rule.success_count}x")
        print(f"  Success Rate: {rule.get_success_rate():.1%}")

# Test 4: Variable unification
print("\n4. VARIABLE UNIFICATION TEST")
print("-" * 70)
from singularis.skyrim.skyrim_world_model import LogicPredicate

pred1 = LogicPredicate("IsHostile", ("?X",), True)
pred2 = LogicPredicate("IsHostile", ("Bandit",), True)
bindings = pred1.unify(pred2)
print(f"Pred1: {pred1}")
print(f"Pred2: {pred2}")
print(f"Unification bindings: {bindings}")
print(f"Success: {bindings is not None}")

# Test generic rule
pred3 = LogicPredicate("IsFriend", ("?NPC",), True)
pred4 = LogicPredicate("IsFriend", ("Lydia",), True)
bindings2 = pred3.unify(pred4)
print(f"\nPred3: {pred3}")
print(f"Pred4: {pred4}")
print(f"Unification bindings: {bindings2}")
print(f"Success: {bindings2 is not None}")

print("\n" + "="*70)
print("✓ Enhanced symbolic logic tests complete!")
print("="*70)
