import socket
import time
from pynput.keyboard import Controller, Key

# --- PASTE YOUR CALIBRATION PROFILE HERE ---
CALIBRATION_PROFILE = {
    'PUNCH_THRESHOLD': 21.38,
    'JUMP_THRESHOLD': 24.10,
    'WALK_SWING_AMPLITUDE': 4.88,
    'WALK_GYRO_NOISE_LIMIT': 0.64,
}
# -------------------------------------------

HOST_IP = '0.0.0.0'
PORT = 12345
GRAVITY_THRESHOLD = 9.0

keyboard = Controller()
last_action_time = 0
action_cooldown = 0.3

# State tracking
is_walking = False
initial_gyro_heading = None
total_rotation = 0.0
last_time = time.time()

print("✅ Dynamic Motion Controller is running.")
print("Face your desired 'forward' direction and start the Android app.")
print("The first data received will set your starting orientation.")

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
                    print(f"▶️ Controller started! 'Forward' direction is set.")

                current_time = time.time()
                delta_time = current_time - last_time
                last_time = current_time

                state = "COMBAT" if abs(y) > GRAVITY_THRESHOLD else "WALKING" if abs(x) > GRAVITY_THRESHOLD else "IDLE"

                # --- Relative Rotation Tracking ---
                # Subtract baseline noise and initial heading to get true rotation
                effective_gyro = gyro_y - initial_gyro_heading
                if abs(effective_gyro) > CALIBRATION_PROFILE['WALK_GYRO_NOISE_LIMIT']:
                    total_rotation += effective_gyro * delta_time

                # Cooldown check
                if current_time - last_action_time < action_cooldown:
                    continue

                if state == "WALKING":
                    # Check for swing amplitude to start/stop walking
                    if abs(z) > CALIBRATION_PROFILE['WALK_SWING_AMPLITUDE'] and not is_walking:
                        is_walking = True
                        print("🚶 WALKING START")
                    elif abs(z) < CALIBRATION_PROFILE['WALK_SWING_AMPLITUDE'] and is_walking:
                        is_walking = False
                        print("🛑 WALKING STOP")

                    if is_walking:
                        direction_key = Key.right if total_rotation < 1.57 else Key.left # Right for +/- 90deg
                        keyboard.press(direction_key)
                        keyboard.release(direction_key) # For continuous movement, you'd manage press/release differently

                    # JUMP (checks X-axis, as it's the vertical axis in this state)
                    if abs(x) > (GRAVITY_THRESHOLD + CALIBRATION_PROFILE['JUMP_THRESHOLD']):
                        print(f"⬆️ JUMP DETECTED (X-Force: {x:.2f})")
                        keyboard.press('z'); keyboard.release('z')
                        last_action_time = current_time

                elif state == "COMBAT":
                    if is_walking: is_walking = False

                    # PUNCH (checks X-axis force)
                    if abs(x) > CALIBRATION_PROFILE['PUNCH_THRESHOLD']:
                        print(f"👊 PUNCH DETECTED (X-Force: {x:.2f})")
                        keyboard.press('x'); keyboard.release('x')
                        last_action_time = current_time

            except (ValueError, IndexError):
                pass