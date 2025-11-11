# Forward-Biased Exploration & Target Tracking

## Overview
Enhanced the Skyrim AGI with forward-prioritized movement and camera-based target scanning using the right stick.

## Key Features

### 1. Forward-Biased Exploration
The AGI now heavily prioritizes forward movement during exploration:

**Movement Distribution:**
- **70%** Forward movement (primary direction)
- **15%** Left strafe
- **15%** Right strafe
- **0%** Backward (only used for evasive maneuvers)

**Benefits:**
- More purposeful exploration
- Better world coverage
- Natural progression through environments
- Reduced aimless wandering

### 2. Camera-Based Target Scanning

Three scanning patterns using right stick:

#### Horizontal Sweep
```
Look left 30° → Sweep right 60° → Return to center
```
- Scans horizon for NPCs, enemies, objects
- Wide field of view coverage
- 60% chance during exploration

#### Vertical Check
```
Look up 20° → Look down 40° → Return to center
```
- Checks elevated positions (towers, cliffs)
- Scans ground level (items, traps)
- Useful for terrain awareness

#### Quick Glance
```
Glance 45° left/right → Return to center
```
- Fast peripheral checks
- Minimal disruption to movement
- Reactive scanning

### 3. Target Tracking System

**`track_moving_target(horizontal_offset, vertical_offset)`**
- Smooth camera adjustments to follow moving objects
- Uses right stick for precise tracking
- Dampened movements (0.5x multiplier) for stability
- Threshold-based activation (>5° offset)

**Use Cases:**
- Following NPCs
- Tracking enemies in combat
- Maintaining line of sight on objectives
- Centering on interactive objects

### 4. Longer Movement Commitments

**Before:** 1.2-2.0 seconds per direction
**Now:** 1.5-2.5 seconds per direction

- More committed to each direction
- Reduces jittery movement
- Better for covering distance
- 4 steps per direction (was 3)

### 5. Reduced Pause Times

**Before:** 0.5 seconds between movements
**Now:** 0.3 seconds between movements

- Faster exploration pace
- More responsive to environment
- Better flow during gameplay

## Integration with Motivation System

All motivation types now default to forward exploration:

- **Curiosity:** Forward exploration to discover new things
- **Competence:** Forward exploration to practice skills
- **Coherence:** Gentle forward exploration (only rest if health < 30)
- **Autonomy:** Forward exploration to exercise agency

## Technical Implementation

### Camera Control
```python
await self.look_horizontal(degrees)  # Right stick X-axis
await self.look_vertical(degrees)    # Right stick Y-axis
```

### Scanning Integration
```python
# During exploration (60% chance per cycle)
await self.scan_for_targets()
```

### Movement Priority
```python
# 70% forward bias
if rand < 0.70:
    current_direction = 'forward'
elif rand < 0.85:
    current_direction = 'left'
else:
    current_direction = 'right'
```

## Expected Behavior

When running the AGI, you should see:
```
[EXPLORE] New direction: forward
[MOVEMENT] Smart forward movement for 2.1s
[SCAN] Horizontal sweep for targets...
[EXPLORE] New direction: forward
[MOVEMENT] Smart forward movement for 1.8s
[SCAN] Quick glance right...
```

The AGI will:
1. Move forward most of the time
2. Frequently scan with camera for targets
3. Occasionally strafe left/right for variety
4. Maintain forward momentum through the world
5. Track any detected moving objects

## Future Enhancements

Potential additions:
- Object detection from visual embeddings
- Automatic target prioritization
- Pathfinding to detected objects
- Combat engagement based on target tracking
- NPC interaction based on proximity detection
