import socket
import time
from pynput.keyboard import Controller, Key

# --- Configuration (UPDATE THESE VALUES FROM CALIBRATE.PY) ---
PUNCH_THRESHOLD = 5.0  # Default value, update this!
JUMP_THRESHOLD = 15.0  # Default value, update this!
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

                    # --- State Detection ---
                    state = None
                    if abs(x) > GRAVITY_THRESHOLD:
                        state = "WALKING"
                    elif abs(y) > GRAVITY_THRESHOLD:
                        state = "COMBAT"

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