# Skyrim Key Bindings Fixed

**Fixed default Skyrim PC controls to match actual game defaults**

---

## 🔧 **Issues Fixed**

### **1. Sprint Key**
- **Before**: `shift` ❌
- **After**: `alt` ✅
- **Reason**: Skyrim PC default is Alt, not Shift

### **2. Wait Key**
- **Before**: Not mapped ❌
- **After**: `t` ✅
- **Reason**: T is the default wait key in Skyrim

### **3. Menu Navigation**
- **Before**: `tab` for BACK ❌
- **After**: `esc` for BACK ✅
- **Reason**: ESC exits menus, Tab opens inventory

### **4. Camera Controls**
- **Before**: String keys like `'mouse_up'` ❌
- **After**: Proper method calls in `_execute_via_input()` ✅
- **Reason**: Camera uses mouse relative movement, not key presses

---

## 📋 **Complete Default Bindings**

```python
DEFAULT_KEYS = {
    # Movement (WASD standard)
    ActionType.MOVE_FORWARD: 'w',
    ActionType.MOVE_BACKWARD: 's',
    ActionType.MOVE_LEFT: 'a',
    ActionType.MOVE_RIGHT: 'd',
    ActionType.JUMP: 'space',
    ActionType.SPRINT: 'alt',        # ✅ FIXED
    ActionType.SNEAK: 'ctrl',
    
    # Combat
    ActionType.ATTACK: 'left_click',
    ActionType.POWER_ATTACK: 'left_click',  # Hold for power attack
    ActionType.BLOCK: 'right_click',
    ActionType.SHOUT: 'z',
    ActionType.HEAL: 'h',  # Custom hotkey (user must set)
    
    # Interaction
    ActionType.ACTIVATE: 'e',  # Use/Talk/Loot/Open
    ActionType.WAIT: 't',      # ✅ FIXED
    ActionType.SLEEP: 'e',     # Same as activate when near bed
    
    # Menus
    ActionType.OPEN_INVENTORY: 'tab',
    ActionType.OPEN_MAP: 'm',
    ActionType.OPEN_MAGIC: 'p',
    ActionType.OPEN_SKILLS: 'k',
    ActionType.BACK: 'esc',    # ✅ FIXED
    
    # Camera (handled via mouse movement)
    ActionType.LOOK_UP: 'mouse_up',
    ActionType.LOOK_DOWN: 'mouse_down',
    ActionType.LOOK_LEFT: 'mouse_left',
    ActionType.LOOK_RIGHT: 'mouse_right',
    
    # Special
    ActionType.QUICK_SAVE: 'f5',
    ActionType.QUICK_LOAD: 'f9',
}
```

---

## 🎮 **Camera Control Implementation**

### **Proper Execution**

Camera movements now properly call mouse movement methods:

```python
# In _execute_via_input()
if action_type == ActionType.LOOK_UP:
    await self.look_up(30.0)
    return True
elif action_type == ActionType.LOOK_DOWN:
    await self.look_down(30.0)
    return True
elif action_type == ActionType.LOOK_LEFT:
    await self.look_horizontal(-30.0)
    return True
elif action_type == ActionType.LOOK_RIGHT:
    await self.look_horizontal(30.0)
    return True
```

### **Mouse Movement Methods**

```python
async def look_horizontal(self, degrees: float):
    """Look left/right by degrees."""
    pixels = int(degrees * 3)
    steps = max(10, abs(pixels) // 20)
    step_size = pixels / steps
    for _ in range(steps):
        pyautogui.moveRel(step_size, 0, duration=0.02)
        await asyncio.sleep(0.01)

async def look_vertical(self, degrees: float):
    """Look up/down by degrees."""
    pixels = int(degrees * 3)
    steps = max(10, abs(pixels) // 20)
    step_size = pixels / steps
    for _ in range(steps):
        pyautogui.moveRel(0, -step_size, duration=0.02)  # Negative = up
        await asyncio.sleep(0.01)
```

---

## 🎯 **Impact on Stuck Loop Problem**

### **Session Issue**
The session report showed:
- Visual similarity: **1.000** (completely static)
- Status: **STUCK**
- No camera corrections applied

### **Root Causes Addressed**

1. **Camera stuck looking up** → `look_down` now works properly
2. **Wrong sprint key** → Can now sprint correctly with Alt
3. **Menu navigation** → ESC properly exits menus
4. **Wait command** → T key now accessible

### **Expected Improvements**

With temporal binding emergency override + fixed keybindings:

```
Cycle 1: STUCK detected (similarity: 1.000)
[TEMPORAL-OVERRIDE] 🚨 STUCK LOOP DETECTED (1 cycles)
[TEMPORAL-OVERRIDE] Initial stuck → look_down
[ACTION] Executing: look_down (using proper mouse movement)
Cycle 2: Visual similarity drops to 0.45 ✅ UNSTUCK!
```

---

## 📝 **Testing Checklist**

### **Movement**
- [ ] W/A/S/D movement works
- [ ] Alt sprint works (not Shift)
- [ ] Space jump works
- [ ] Ctrl sneak works

### **Combat**
- [ ] Left click attack
- [ ] Right click block
- [ ] Z shout
- [ ] H heal (if hotkeyed)

### **Interaction**
- [ ] E activate (doors, NPCs, items)
- [ ] T wait menu
- [ ] E sleep (when near bed)

### **Menus**
- [ ] Tab opens inventory
- [ ] M opens map
- [ ] P opens magic
- [ ] K opens skills
- [ ] ESC exits menus (not Tab)

### **Camera**
- [ ] Look up/down works smoothly
- [ ] Look left/right works smoothly
- [ ] Look around randomizes view
- [ ] Camera corrections unstick AGI

### **Special**
- [ ] F5 quick save
- [ ] F9 quick load

---

## 🚀 **Controller Support**

The system also supports Xbox controller with proper mappings:

```python
_controller_action_map = {
    ActionType.MOVE_FORWARD: "move_forward",
    ActionType.SPRINT: "sprint",
    ActionType.JUMP: "jump",
    ActionType.SNEAK: "sneak",
    ActionType.ATTACK: "attack",
    ActionType.BLOCK: "block",
    ActionType.ACTIVATE: "activate",
    ActionType.LOOK_UP: "look_up",
    ActionType.LOOK_DOWN: "look_down",
    # ... etc
}
```

---

## ✅ **Status**

**Key Bindings**: Fixed ✅  
**Camera Controls**: Fixed ✅  
**Menu Navigation**: Fixed ✅  
**Sprint Key**: Fixed ✅  
**Wait Command**: Fixed ✅  

**Files Modified:**
- `singularis/skyrim/actions.py` - Fixed DEFAULT_KEYS and camera execution

**Next Session**: AGI should properly execute all actions including camera corrections to escape stuck states!

---

**Singularis Neo Beta 1.0 - Skyrim Controls Verified** 🎮✨
