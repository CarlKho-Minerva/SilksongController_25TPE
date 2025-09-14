import socket
import time
import math
import statistics
from collections import deque
from pynput.keyboard import Controller, Key

# --- PASTE YOUR CALIBRATION PROFILE HERE ---
CALIBRATION_PROFILE = {
    'PUNCH_THRESHOLD': 10.0,
    'JUMP_THRESHOLD': 12.0,
    'WALK_SWING_AMPLITUDE': 3.0,
    'WALK_GYRO_NOISE_LIMIT': 0.5,
}
# -------------------------------------------

HOST_IP = '0.0.0.0'
PORT = 12345
GRAVITY_CONSTANT = 9.81  # Earth's gravity constant
GRAVITY_THRESHOLD = 9.0

keyboard = Controller()
last_action_time = 0
action_cooldown = 0.3

# State tracking with stability buffer
is_walking = False
walking_key_pressed = False  # Track if we're currently holding a walking key
current_walking_key = None   # Track which key is currently pressed
jump_key_pressed = False     # Track if jump key is currently held
initial_gyro_heading = None
total_rotation = 0.0
last_time = time.time()
current_state = "IDLE"
state_buffer = deque(maxlen=5)  # Rolling buffer for state stability
last_action = "NONE"
last_action_value = 0.0

def update_status_display(state, facing_dir, rotation_deg, last_action, last_value):
    """Display clean, single-line status update"""
    print(f"\rSTATE: {state:7} | FACING: {facing_dir} ({rotation_deg:4.0f}°) | LAST ACTION: {last_action} ({last_value:.1f})", end="", flush=True)

def determine_state_from_sensors(x, y, z):
    """Determine raw state from sensor readings"""
    if abs(y) > GRAVITY_THRESHOLD:
        return "COMBAT"
    elif abs(x) > GRAVITY_THRESHOLD:
        return "WALKING"
    else:
        return "IDLE"

def get_stable_state(raw_state, state_buffer):
    """Apply state stability buffer - requires 4/5 consensus to change state"""
    state_buffer.append(raw_state)

    # Count occurrences of each state in buffer
    walking_count = state_buffer.count("WALKING")
    combat_count = state_buffer.count("COMBAT")
    idle_count = state_buffer.count("IDLE")

    # Require 4/5 consensus to change state (provides stickiness)
    if walking_count >= 4:
        return "WALKING"
    elif combat_count >= 4:
        return "COMBAT"
    elif idle_count >= 4:
        return "IDLE"
    else:
        # No consensus, keep current state
        return None  # Will use previous stable state


def manage_sustained_jump(x, y, z, jerk_force, jump_threshold):
    """Handle sustained jump based on acceleration patterns"""
    global jump_key_pressed, last_action, last_action_value, last_action_time

    total_acceleration = math.sqrt(x**2 + y**2 + z**2)
    current_time = time.time()

    # JUMP START: Strong upward jerk detected
    if jerk_force > jump_threshold and not jump_key_pressed:
        keyboard.press('z')
        jump_key_pressed = True
        last_action = "JUMP_START"
        last_action_value = jerk_force
        last_action_time = current_time
        return "JUMP_START"

    # JUMP CONTINUE: Low total acceleration indicates "airborne" state
    # (When phone is suspended/floating, total acceleration approaches gravity)
    elif jump_key_pressed and total_acceleration < 12.0:  # Slightly above gravity
        # Keep holding jump key while "airborne"
        last_action = "JUMP_AIRBORNE"
        last_action_value = total_acceleration
        return "JUMP_CONTINUE"

    # JUMP END: High acceleration spike indicates landing or strong movement
    elif jump_key_pressed and (jerk_force > jump_threshold * 0.7 or total_acceleration > 15.0):
        keyboard.release('z')
        jump_key_pressed = False
        last_action = "JUMP_LAND"
        last_action_value = total_acceleration
        last_action_time = current_time
        return "JUMP_END"

    return None


def manage_walking_key_press(should_walk, direction_key):
    """Handle sustained key press for walking"""
    global walking_key_pressed, current_walking_key

    if should_walk and not walking_key_pressed:
        # Start walking - press and hold key
        keyboard.press(direction_key)
        walking_key_pressed = True
        current_walking_key = direction_key
        return "WALK_KEY_PRESS"
    elif should_walk and walking_key_pressed and current_walking_key != direction_key:
        # Direction changed - release old key, press new key
        keyboard.release(current_walking_key)
        keyboard.press(direction_key)
        current_walking_key = direction_key
        return "WALK_DIRECTION_CHANGE"
    elif not should_walk and walking_key_pressed:
        # Stop walking - release key
        keyboard.release(current_walking_key)
        walking_key_pressed = False
        current_walking_key = None
        return "WALK_KEY_RELEASE"

    return None  # No key state change needed
print("✅ Dynamic Motion Controller is running.")
print("Face your desired 'forward' direction and start the Android app.")
print("The first data received will set your starting orientation.")
print()  # Empty line for status display

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST_IP, PORT))
    while True:
        data, _ = s.recvfrom(1024)
        message = data.decode().strip()

        if message.startswith("SENSOR:"):
            try:
                parts = message.replace("SENSOR:", "").split(',')
                x, y, z, gyro_y = [float(p) for p in parts]

                # --- Set Initial "Forward" Direction ---
                if initial_gyro_heading is None:
                    initial_gyro_heading = gyro_y
                    print("▶️ Controller started! 'Forward' direction is set.")
                    print()  # Empty line for status display

                current_time = time.time()
                delta_time = current_time - last_time
                last_time = current_time

                # --- STATE STABILITY BUFFER IMPLEMENTATION ---
                raw_state = determine_state_from_sensors(x, y, z)
                stable_state = get_stable_state(raw_state, state_buffer)

                if stable_state is not None:
                    current_state = stable_state

                # --- Relative Rotation Tracking ---
                effective_gyro = gyro_y - initial_gyro_heading
                gyro_limit = CALIBRATION_PROFILE['WALK_GYRO_NOISE_LIMIT']
                if abs(effective_gyro) > gyro_limit:
                    total_rotation += effective_gyro * delta_time

                # Calculate facing direction and rotation degrees
                rotation_deg = math.degrees(total_rotation)
                facing_dir = "RIGHT" if total_rotation < 1.57 else "LEFT"

                # Cooldown check
                if current_time - last_action_time < action_cooldown:
                    # Still update status display even during cooldown
                    update_status_display(current_state, facing_dir,
                                         rotation_deg, last_action,
                                         last_action_value)
                    continue

                if current_state == "WALKING":
                    walk_amp = CALIBRATION_PROFILE['WALK_SWING_AMPLITUDE']
                    # Check for swing amplitude to determine if actively walking
                    currently_walking = abs(z) > walk_amp

                    # Determine direction based on rotation
                    direction_key = (Key.right if total_rotation < 1.57
                                   else Key.left)

                    # Manage sustained key press for walking
                    key_action = manage_walking_key_press(currently_walking, direction_key)
                    if key_action:
                        last_action = key_action
                        last_action_value = abs(z)

                    # Update walking state for display
                    if currently_walking != is_walking:
                        is_walking = currently_walking

                    # ENHANCED JUMP PHYSICS - Sustained jump based on acceleration patterns
                    magnitude = math.sqrt(x**2 + y**2 + z**2)
                    jerk_force = magnitude - GRAVITY_CONSTANT
                    jump_threshold = CALIBRATION_PROFILE['JUMP_THRESHOLD']

                    # Use sustained jump logic instead of single tap
                    jump_action = manage_sustained_jump(x, y, z, jerk_force, jump_threshold)
                    if jump_action and not jump_action.startswith("JUMP_CONTINUE"):
                        # Only update timing for start/end actions, not continue
                        last_action_time = current_time

                elif current_state == "COMBAT":
                    if is_walking:
                        is_walking = False

                    # CORRECTED PUNCH PHYSICS - Measure actual jerk force
                    magnitude = math.sqrt(x**2 + y**2 + z**2)
                    jerk_force = magnitude - GRAVITY_CONSTANT
                    punch_threshold = CALIBRATION_PROFILE['PUNCH_THRESHOLD']

                    if jerk_force > punch_threshold:
                        keyboard.press('x')
                        keyboard.release('x')
                        last_action = "PUNCH"
                        last_action_value = jerk_force
                        last_action_time = current_time

                # Update real-time status display
                update_status_display(current_state, facing_dir, rotation_deg,
                                     last_action, last_action_value)

            except (ValueError, IndexError):
                pass