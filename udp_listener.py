import socket
import time
from pynput.keyboard import Controller, Key

# --- Configuration (UPDATE THESE VALUES FROM CALIBRATE.PY) ---
PUNCH_THRESHOLD = 16.33  # Default value, update this!
JUMP_THRESHOLD = 3.73    # Default value, update this!
# -----------------------------------------------------------

HOST_IP = '0.0.0.0'
PORT = 12345
GRAVITY_THRESHOLD = 9.0

keyboard = Controller()
last_action_time = 0
action_cooldown = 0.3

# State tracking
facing_right = True
is_walking = False
total_rotation = 0.0
last_time = time.time()
current_state = None  # Track the current confirmed state
state_samples = []    # Buffer recent gravity readings for stability

print("✅ State-Aware Controller is running.")
print("="*50)
print("STANCE 1: Walking/Jumping (Horizontal)")
print("  • Hold phone horizontally, screen facing your body")
print("  • Walk: Natural pendulum swing")
print("  • Jump: Sharp upward jerk (only works in walking stance)")
print("  • Turn: Rotate your body 180 degrees")
print("")
print("STANCE 2: Attacking (Vertical)")
print("  • Hold phone vertically, screen facing left")
print("  • Attack: Forward punch motion")
print("="*50)
print("Waiting for sensor data...")

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST_IP, PORT))
    while True:
        try:
            data, _ = s.recvfrom(1024)
            message = data.decode().strip()

            if message.startswith("SENSOR:"):
                try:
                    parts = message.replace("SENSOR:", "").split(',')
                    if len(parts) >= 4:
                        x, y, z, gyro_y = [float(p) for p in parts]
                    else:
                        # Fallback for old 3-value format
                        x, y, z = [float(p) for p in parts]
                        gyro_y = 0.0

                    current_time = time.time()
                    delta_time = current_time - last_time
                    last_time = current_time

                    # --- State Detection with Stability ---
                    # Use a more sophisticated approach that considers recent readings
                    # and doesn't change state based on temporary gesture spikes

                    # Add current reading to buffer (keep last 5 readings)
                    state_samples.append((x, y))
                    if len(state_samples) > 5:
                        state_samples.pop(0)

                    # Calculate average gravity readings (ignoring extreme spikes)
                    if len(state_samples) >= 3:
                        # Remove the highest and lowest to filter spikes
                        x_values = [abs(sample[0]) for sample in state_samples]
                        y_values = [abs(sample[1]) for sample in state_samples]
                        x_values.sort()
                        y_values.sort()
                        # Use middle values
                        avg_x = sum(x_values[1:-1]) / max(1, len(x_values) - 2)
                        avg_y = sum(y_values[1:-1]) / max(1, len(y_values) - 2)

                        # Determine state based on stable gravity readings
                        if avg_x > 8.0 and avg_x > avg_y + 2.0:
                            new_state = "WALKING"
                        elif avg_y > 8.0 and avg_y > avg_x + 2.0:
                            new_state = "COMBAT"
                        else:
                            new_state = current_state  # Keep current state if unclear

                        # Only change state if we have a clear reading or no current state
                        if current_state is None or new_state != current_state:
                            if new_state in ["WALKING", "COMBAT"]:
                                current_state = new_state

                        state = current_state
                    else:
                        state = current_state  # Keep current state until we have enough samples

                    # --- Rotation Tracking ---
                    total_rotation += gyro_y * delta_time
                    if abs(total_rotation) > 3.14: # ~180 degrees
                        facing_right = not facing_right
                        direction = "RIGHT" if facing_right else "LEFT"
                        print(f"🔄 TURN DETECTED! Now facing {direction}")
                        total_rotation = 0.0
                        last_action_time = current_time

                    # Cooldown check
                    if current_time - last_action_time < action_cooldown:
                        continue

                    # --- Execute Logic Based on State ---
                    if state == "WALKING":
                        if not is_walking:
                            walk_key = Key.right if facing_right else Key.left
                            direction = "RIGHT" if facing_right else "LEFT"
                            print(f"🚶 WALKING START (Facing {direction})")
                            keyboard.press(walk_key)
                            is_walking = True

                        # JUMP (only allowed while walking)
                        if y > JUMP_THRESHOLD:
                            print(f"⬆️  JUMP DETECTED (Y-Force: {y:.2f})")
                            keyboard.press(Key.space)
                            keyboard.release(Key.space)
                            last_action_time = current_time

                    elif state == "COMBAT":
                        if is_walking:
                            print("🛑 WALKING STOP (Entering combat stance)")
                            keyboard.release(Key.right)
                            keyboard.release(Key.left)
                            is_walking = False

                        # PUNCH (X-force while Y feels gravity)
                        if abs(x) > PUNCH_THRESHOLD:
                            print(f"👊 PUNCH DETECTED (X-Force: {x:.2f})")
                            keyboard.press('x')
                            keyboard.release('x')
                            last_action_time = current_time

                    else: # In-between states (e.g., transitions)
                        if is_walking:
                            print("🛑 WALKING STOP (No clear orientation)")
                            keyboard.release(Key.right)
                            keyboard.release(Key.left)
                            is_walking = False

                except (ValueError, IndexError) as e:
                    # Skip malformed messages
                    continue

        except KeyboardInterrupt:
            print("\n🛑 Controller stopped by user.")
            if is_walking:
                keyboard.release(Key.right)
                keyboard.release(Key.left)
            break
        except Exception as e:
            print(f"Error: {e}")
            continue