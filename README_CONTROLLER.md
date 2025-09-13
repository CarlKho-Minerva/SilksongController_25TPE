# SilksongController - State-Aware Motion Controller

A comprehensive motion control system that transforms your Android phone into a context-aware game controller using accelerometer and gyroscope sensors.

## Features

### 🎯 State-Aware Detection
- **Walking State**: Phone held horizontally - gravity detected on X-axis
- **Combat State**: Phone held vertically - gravity detected on Y-axis
- **Automatic Transition**: Seamlessly switches between states based on orientation

### 🔄 Rotation Tracking
- Uses gyroscope data to detect when you turn around
- Automatically changes walking direction when you rotate 180°
- No manual controls needed for direction changes

### 📊 Data-Driven Calibration
- Personal gesture threshold calibration
- Records multiple samples for accuracy
- Generates ready-to-use configuration values

### 🎮 Context-Aware Controls
- **Walking State**: Natural pendulum motion for movement, upward jerk for jumping
- **Combat State**: Forward punch motion for attacks
- **Smart Gestures**: Jump only works in walking state, punch only in combat state

## System Architecture

```
┌─────────────────┐    UDP     ┌──────────────────┐    pynput    ┌─────────┐
│  Android App    │ ---------> │ Python Controller │ -----------> │  Game   │
│                 │  (WiFi)    │                  │ (Keyboard)   │         │
│ • Accelerometer │            │ • State Machine  │              │         │
│ • Gyroscope     │            │ • Gesture Recog  │              │         │
│ • UDP Sender    │            │ • Calibration    │              │         │
└─────────────────┘            └──────────────────┘              └─────────┘
```

## Quick Start Guide

### Step 1: Prepare Your Environment

1. **Install Python Dependencies**:
   ```bash
   pip install pynput statistics
   ```

2. **Set Up Network**:
   - Ensure your Android phone and Mac are on the same WiFi network
   - Find your Mac's IP address (System Settings > Wi-Fi > Details...)

### Step 2: Calibrate Your Gestures

1. **Build and run the Android app** on your phone
2. **Enter your Mac's IP address** in the app
3. **Tap "Start"** to begin streaming sensor data
4. **Run the calibration script**:
   ```bash
   python3 calibrate.py
   ```
5. **Follow the prompts** to record your personal gesture thresholds:
   - Record 5 punch gestures while holding phone vertically
   - Record 5 jump gestures while holding phone horizontally
6. **Copy the generated threshold values** into `udp_listener.py`

### Step 3: Start Gaming

1. **Run the main controller**:
   ```bash
   python3 udp_listener.py
   ```
2. **Start your game** (e.g., Hollow Knight)
3. **Begin motion control**!

## Usage Guide

### Walking State (Horizontal Hold)
```
📱 Phone Position: Horizontal, screen facing your body
🎯 Purpose: Movement and jumping
```
- **Walk**: Start a natural pendulum-like swing motion
  - Controller automatically detects rhythm and holds arrow key
  - Direction depends on which way you're facing
- **Jump**: Sharp upward jerk motion
  - Only works in walking state for safety
- **Turn Around**: Physically rotate your body 180°
  - Gyroscope detects rotation and switches walking direction

### Combat State (Vertical Hold)
```
📱 Phone Position: Vertical, screen facing left (like holding a sword hilt)
🎯 Purpose: Attacking
```
- **Attack**: Forward punch motion
  - Only works in combat state to prevent accidental attacks
  - Uses X-axis acceleration while Y-axis feels gravity

### State Transitions
- **Automatic Detection**: Based on gravity orientation
- **Smooth Switching**: Walking stops when entering combat state
- **Visual Feedback**: Console shows current state and actions

## Configuration

### Threshold Values (from calibration)
```python
PUNCH_THRESHOLD = 5.0   # Update from calibrate.py
JUMP_THRESHOLD = 15.0   # Update from calibrate.py
```

### System Constants
```python
GRAVITY_THRESHOLD = 9.0  # Gravity detection sensitivity
ACTION_COOLDOWN = 0.3    # Seconds between actions
```

### Key Mappings
- **Walk**: Left/Right Arrow keys
- **Jump**: Spacebar
- **Attack**: 'x' key

## Troubleshooting

### Android App Issues
- **"Please enter an IP address"**: Enter your Mac's IP in the text field
- **"Network error"**: Check WiFi connection and IP address
- **App crashes**: Ensure all permissions are granted

### Python Script Issues
- **"Address already in use"**: Stop any running UDP listeners first
- **"No module named 'pynput'"**: Install dependencies with `pip install pynput`
- **No sensor data received**: Check Android app is started and IP is correct

### Gesture Detection Issues
- **Gestures not detected**: Run calibration script to set personal thresholds
- **Wrong state detected**: Hold phone in correct orientation (horizontal vs vertical)
- **Rotation not working**: Ensure gyroscope data is being sent (4-value format)

## Technical Details

### Android App (MainActivity.kt)
- **Sensors**: Accelerometer + Gyroscope at SENSOR_DELAY_GAME rate
- **Data Format**: `SENSOR:x,y,z,gyro_y` (4 floating-point values)
- **Throttling**: 33 FPS (30ms intervals) to prevent network flooding
- **Threading**: All networking on IO dispatcher via Kotlin Coroutines

### Python Controller (udp_listener.py)
- **State Machine**: Gravity-based state detection
- **Rotation Integration**: Gyroscope Y-axis integrated over time
- **Gesture Recognition**: Threshold-based with cooldown timers
- **Error Handling**: Graceful parsing of malformed messages

### Calibration System (calibrate.py)
- **Sample Collection**: 2-second recording windows per gesture
- **Threshold Calculation**: 80% of average peak values for reliability
- **Format Support**: Handles both 3-value and 4-value sensor formats

## Development Notes

### Message Protocol
```
Old Format: SENSOR:x,y,z
New Format: SENSOR:x,y,z,gyro_y
```

### State Detection Algorithm
```python
if abs(x) > GRAVITY_THRESHOLD:
    state = "WALKING"      # Phone horizontal
elif abs(y) > GRAVITY_THRESHOLD:
    state = "COMBAT"       # Phone vertical
else:
    state = "TRANSITION"   # In-between
```

### Rotation Tracking
```python
total_rotation += gyro_y * delta_time
if abs(total_rotation) > 3.14:  # ~180 degrees
    facing_right = not facing_right
    total_rotation = 0.0
```

## Contributing

When making changes:
1. Test with both old (3-value) and new (4-value) message formats
2. Validate state detection with different phone orientations
3. Ensure calibration script generates reasonable thresholds
4. Test end-to-end functionality with actual games

## License

This project is part of the SilksongController system for educational purposes.