# GitHub Copilot Instructions for SilksongController

## Project Overview

This is a **motion-based game controller** that transforms Android phones into Hollow Knight: Silksong controllers via UDP communication between Android sensors and Python backend. The system uses **state-dependent gesture recognition** with orientation-based context switching.

## Core Architecture

### Two-Component System
- **Android App** (`AndroidStudio/`): Kotlin app sending sensor data (`SENSOR:x,y,z,gyro_y` format) over UDP
- **Python Backend**: Real-time gesture processing with state machine architecture

### State Machine Logic
```python
# Phone orientation determines available controls
if abs(x) > GRAVITY_THRESHOLD:  # Horizontal = walking state
    # Enable: movement (left/right arrows), jumping (z key)
elif abs(y) > GRAVITY_THRESHOLD:  # Vertical = combat state
    # Enable: punching (x key) only
```

### Critical Patterns

#### 1. Calibration-First Workflow
Always run `python3 calibrate.py` before implementing gesture features:
- Records user-specific thresholds for punch/jump/walk gestures
- Outputs copy-paste `CALIBRATION_PROFILE` dict for `udp_listener.py`
- Gesture data stored in `gesture_data/*.json` with accelerometer + gyroscope readings

#### 2. UDP Communication Protocol
```kotlin
// Android sends 4-value format every 30ms
"SENSOR:${accel_x},${accel_y},${accel_z},${gyro_y}"
```

#### 3. Gravity-Based State Detection
```python
# Core state logic - requires 4/5 consensus in rolling buffer
GRAVITY_THRESHOLD = 9.0  # Earth gravity ~9.81, with tolerance
```

## Key Development Commands

```bash
# Start controller (requires calibration first)
python3 udp_listener.py

# Generate user calibration profile
python3 calibrate.py

# Android build (from AndroidStudio/ directory)
./gradlew assembleDebug
```

## Important Conventions

### File Structure Patterns
- `udp_listener.py`: Main controller with state machine
- `calibrate.py`: Interactive threshold generation
- `gesture_data/`: JSON files with raw sensor recordings
- `MainActivity.kt`: Android sensor data transmission

### State Management
- **Stability Buffer**: 5-frame rolling buffer prevents state flicker
- **Dynamic Zero Point**: First gyroscope reading sets "forward" direction
- **Sustained Actions**: Jump uses press/hold/release pattern, not single tap

### Android Sensor System
- Wake lock prevents sleep during controller use: 'FLAG_KEEP_SCREEN_ON*
- Coroutine-based UDP sending every 30ms for smooth data flow
- Multiple sensor fusion: accelerometer + gyroscope + gravity sensors

**Available Sensors** (all with 3-axis data):
- `TYPE_ACCELEROMETER`: Raw acceleration including gravity
- `TYPE_GYROSCOPE`: Angular velocity (rotation rates)
- `TYPE_LINEAR_ACCELERATION`: Acceleration minus gravity
- `TYPE_GRAVITY`: Gravity vector only

**Sensor Capabilities**:
- All sensors register at `SENSOR_DELAY_GAME` (fastest)
- Data stored in separate FloatArray(3) for each sensor type
- Wake lock prevents sleep: `FLAG_KEEP_SCREEN_ON`
- Coroutine-based UDP transmission every 30ms

## Critical Implementation Gotchas

### 1. **NEVER Modify Existing Scripts - Always Preserve**
- Adding new scripts instead of preserving existing ones breaks the system
- Always extend/preserve existing functionality rather than replacing
- Maintain all existing calibration thresholds and state logic

### 2. **UDP Protocol Mismatch Warning**
```kotlin
// Android currently sends 12 values (4 sensors × 3 axes)
"SENSOR:${accel_x},${accel_y},${accel_z},${gyro_x},${gyro_y},${gyro_z}..."

// But Python expects exactly 4 values
x, y, z, gyro_y = [float(p) for p in parts]
```
**Fix Required**: Align Android transmission with Python parsing

### 3. **Development Workflow**
```bash
# 1. Calibrate first (generates thresholds)
python3 calibrate.py

# 2. Start Python listener
python3 udp_listener.py

# 3. Android Studio: Hit "Run" button (don't use gradlew)
# 4. Enter Python machine's IP address in Android app
```

### 4. **Essential Preservation Rules**
- **Never hardcode gesture thresholds** - always use calibration system
- **Phone orientation determines state** - X/Y axis roles swap between horizontal/vertical
- **Jerk force calculation**: `magnitude - GRAVITY_CONSTANT` for punch/jump detection
- **State stability**: 4/5 consensus required in rolling buffer to prevent flicker