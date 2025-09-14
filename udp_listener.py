import socket
import time
import math
from collections import deque
from pynput.keyboard import Controller, Key

# --- PASTE YOUR CALIBRATION VALUES HERE ---
PUNCH_THRESHOLD = 21.38
JUMP_THRESHOLD = 24.10
# -------------------------------------------

HOST_IP = '0.0.0.0'
PORT = 12345
GRAVITY_THRESHOLD = 8.0  # Allow a little tolerance

keyboard = Controller()
last_action_time = 0
action_cooldown = 0.4

# State tracking
facing_right = True
is_walking = False
total_rotation_rad = 0.0
last_time = time.time()

# State Stability Buffer
state_buffer = deque(maxlen=5)
current_state = "IDLE"

print("✅ Dynamic Motion Controller is running.")
print("Face 'forward' and start the Android app to set initial orientation.")

def print_status(state, rotation_deg, last_action):
    """Prints a single, updating status line."""
    facing = "RIGHT" if facing_right else "LEFT"
    status_string = f"STATE: {state:<10} | FACING: {facing} ({rotation_deg:4.0f}°) | LAST ACTION: {last_action:<15}"
    print(status_string, end='\r')

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST_IP, PORT))
    last_action = "None"
    
    while True:
        data, _ = s.recvfrom(1024)
        message = data.decode().strip()

        if message.startswith("SENSOR:"):
            try:
                parts = message.replace("SENSOR:", "").split(',')
                x, y, z, gyro_y = [float(p) for p in parts]
                
                current_time = time.time()
                delta_time = current_time - last_time
                last_time = current_time

                # --- State Detection with Stability Buffer ---
                # Determine potential state from this single frame
                potential_state = "IDLE"
                if abs(x) > GRAVITY_THRESHOLD:
                    potential_state = "WALKING"
                elif abs(y) > GRAVITY_THRESHOLD:
                    potential_state = "COMBAT"
                state_buffer.append(potential_state)

                # Confirm state only if it's consistent
                if state_buffer.count("WALKING") >= 4:
                    current_state = "WALKING"
                elif state_buffer.count("COMBAT") >= 4:
                    current_state = "COMBAT"
                
                # --- Rotation Tracking ---
                total_rotation_rad += gyro_y * delta_time
                if abs(total_rotation_rad) > 3.14: # 180 degrees in radians
                    facing_right = not facing_right
                    total_rotation_rad = 0.0
                    last_action = "TURN"
                
                rotation_degrees = math.degrees(total_rotation_rad)
                print_status(current_state, rotation_degrees, last_action)

                if current_time - last_action_time < action_cooldown:
                    continue

                # --- Execute Logic Based on Confirmed State ---
                if current_state == "WALKING":
                    if not is_walking:
                        walk_key = Key.right if facing_right else Key.left
                        keyboard.press(walk_key)
                        is_walking = True

                    # JUMP (magnitude of force beyond gravity)
                    magnitude = math.sqrt(x**2 + y**2 + z**2)
                    jerk_force = magnitude - GRAVITY_THRESHOLD
                    if jerk_force > JUMP_THRESHOLD:
                        keyboard.press(Key.space); keyboard.release(Key.space)
                        last_action = f"JUMP ({jerk_force:.2f})"
                        last_action_time = current_time

                elif current_state == "COMBAT":
                    if is_walking:
                        keyboard.release(Key.right); keyboard.release(Key.left)
                        is_walking = False

                    # PUNCH (force on X-axis)
                    if abs(x) > PUNCH_THRESHOLD:
                        keyboard.press('x'); keyboard.release('x')
                        last_action = f"PUNCH ({abs(x):.2f})"
                        last_action_time = current_time
                
                elif is_walking: # If state becomes IDLE or something else, stop walking
                    keyboard.release(Key.right); keyboard.release(Key.left)
                    is_walking = False

            except (ValueError, IndexError, KeyboardInterrupt):
                break

print("\nController stopped.")