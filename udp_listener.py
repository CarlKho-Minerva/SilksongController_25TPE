import socket
import math # We need this for the square root function
import time # We need this to manage the cooldown

# This library allows our script to press keys
from pynput.keyboard import Controller, Key

# --- Configuration ---
HOST_IP = '0.0.0.0'
PORT = 12345

# --- Gesture Tuning ---
# The force required to register a punch. You WILL need to adjust this!
PUNCH_THRESHOLD = 25.0

# Walking thresholds (tilt detection)
WALK_THRESHOLD = 3.0  # X-axis tilt to start walking
WALK_STOP_THRESHOLD = 1.5  # X-axis tilt to stop walking

# Jump threshold (upward acceleration)
JUMP_THRESHOLD = 15.0  # Y-axis spike for jumping

# Turn around threshold (quick direction change)
TURN_THRESHOLD = 8.0  # How much X-axis must change quickly
TURN_TIME_WINDOW = 0.3  # Time window to detect direction change

# Cooldowns in seconds
PUNCH_COOLDOWN_S = 0.5
JUMP_COOLDOWN_S = 0.3
TURN_COOLDOWN_S = 0.8
# ---------------------

# Create a keyboard controller object
keyboard = Controller()

# State tracking variables
last_punch_time = 0
last_jump_time = 0
last_turn_time = 0

# Walking state
is_walking = False
walking_direction = None  # 'left' or 'right'

# Character facing direction (True = right, False = left)
facing_right = True

# Turn detection variables
recent_x_values = []  # Store recent X values for turn detection
MAX_RECENT_VALUES = 10

def detect_turn_around(x_value):
    """Detect if user is doing a quick turn-around gesture"""
    global recent_x_values, last_turn_time, facing_right

    current_time = time.time()
    if (current_time - last_turn_time) < TURN_COOLDOWN_S:
        return False

    # Add current X value to recent values
    recent_x_values.append(x_value)
    if len(recent_x_values) > MAX_RECENT_VALUES:
        recent_x_values.pop(0)

    # Need at least 5 values to detect turn
    if len(recent_x_values) < 5:
        return False

    # Check for rapid direction change
    min_x = min(recent_x_values[-5:])
    max_x = max(recent_x_values[-5:])

    # If there's a big swing in X-axis quickly, it's a turn
    if abs(max_x - min_x) > TURN_THRESHOLD:
        print(f"TURN AROUND DETECTED! (X swing: {max_x:.1f} to {min_x:.1f})")

        # Toggle facing direction
        facing_right = not facing_right
        direction_str = "RIGHT" if facing_right else "LEFT"
        print(f"Now facing: {direction_str}")

        # Press the opposite direction briefly to turn around
        turn_key = Key.left if facing_right else Key.right
        keyboard.press(turn_key)
        time.sleep(0.1)  # Brief press
        keyboard.release(turn_key)

        last_turn_time = current_time
        return True

    return False

def handle_walking(x_value):
    """Handle walking based on phone tilt"""
    global is_walking, walking_direction

    # Determine desired walking direction based on tilt
    if abs(x_value) < WALK_STOP_THRESHOLD:
        # Not tilted enough - stop walking
        if is_walking:
            # Release the current walking key
            release_key = Key.right if walking_direction == 'right' else Key.left
            keyboard.release(release_key)
            print(f"STOP WALKING")
            is_walking = False
            walking_direction = None

    elif x_value > WALK_THRESHOLD:
        # Tilted right - walk right
        new_direction = 'right'
        if not is_walking or walking_direction != new_direction:
            # Stop previous walking if different direction
            if is_walking and walking_direction != new_direction:
                old_key = Key.left if walking_direction == 'left' else Key.right
                keyboard.release(old_key)

            # Start walking right
            keyboard.press(Key.right)
            print(f"WALKING RIGHT (X tilt: {x_value:.2f})")
            is_walking = True
            walking_direction = new_direction

    elif x_value < -WALK_THRESHOLD:
        # Tilted left - walk left
        new_direction = 'left'
        if not is_walking or walking_direction != new_direction:
            # Stop previous walking if different direction
            if is_walking and walking_direction != new_direction:
                old_key = Key.right if walking_direction == 'right' else Key.left
                keyboard.release(old_key)

            # Start walking left
            keyboard.press(Key.left)
            print(f"WALKING LEFT (X tilt: {x_value:.2f})")
            is_walking = True
            walking_direction = new_direction

print(f"✅ Enhanced Silksong Controller is running.")
print(f"Listening for motion data on port {PORT}...")
print(f"Gestures:")
print(f"  • Punch Forward: Attack (X key)")
print(f"  • Tilt Left/Right: Walk (Arrow keys)")
print(f"  • Quick Flip: Turn Around")
print(f"  • Jerk Up: Jump (Spacebar)")
print("--------------------------------------------------")

# --- Main Program ---
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST_IP, PORT))

    while True:
        data, addr = s.recvfrom(1024)
        message = data.decode().strip()

        # Check if the message is sensor data
        if message.startswith("SENSOR:"):
            try:
                # 1. PARSE the message to get the numbers
                parts = message.replace("SENSOR:", "").split(',')
                x = float(parts[0])
                y = float(parts[1])
                z = float(parts[2])

                # 2. CALCULATE the magnitude of the acceleration
                magnitude = math.sqrt(x**2 + y**2 + z**2)

                # 3. CHECK for different gestures
                current_time = time.time()

                # PUNCH DETECTION (forward thrust)
                if magnitude > PUNCH_THRESHOLD and (current_time - last_punch_time) > PUNCH_COOLDOWN_S:
                    print(f"PUNCH DETECTED! (Magnitude: {magnitude:.2f}) -> Pressing 'X'")
                    keyboard.press('x')
                    keyboard.release('x')
                    last_punch_time = current_time

                # JUMP DETECTION (upward jerk)
                elif y > JUMP_THRESHOLD and (current_time - last_jump_time) > JUMP_COOLDOWN_S:
                    print(f"JUMP DETECTED! (Y-axis: {y:.2f}) -> Pressing SPACE")
                    keyboard.press(Key.space)
                    keyboard.release(Key.space)
                    last_jump_time = current_time

                # TURN AROUND DETECTION (quick X-axis change)
                elif not detect_turn_around(x):
                    # WALKING DETECTION (only if not turning around)
                    handle_walking(x)

            except (ValueError, IndexError):
                # If the message is malformed, just ignore it and continue
                pass
