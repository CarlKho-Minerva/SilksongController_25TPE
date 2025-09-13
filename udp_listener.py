import socket
import math
import time
from collections import deque # A special list that is efficient for adding/removing from both ends

# This library allows our script to press keys
from pynput.keyboard import Controller, Key

# --- Configuration ---
HOST_IP = '0.0.0.0'
PORT = 12345

# --- Gesture Tuning ---
# A forward punch is a strong negative Z acceleration.
PUNCH_THRESHOLD = 20.0
JUMP_THRESHOLD = 15.0

# --- Rhythmic Walking Tuning (Now on Z-axis) ---
# A buffer to store the history of Z-axis acceleration values (forward/backward swing)
SWING_HISTORY = deque(maxlen=20) # Store roughly 2/3 of a second of data
# The value must swing above/below this threshold to count
SWING_AMPLITUDE_THRESHOLD = 2.5
# How many times the value must cross zero in the history to start walking
SWING_CROSSING_THRESHOLD = 3

# Cooldowns in seconds
PUNCH_COOLDOWN_S = 0.5
JUMP_COOLDOWN_S = 0.5
# ---------------------

# Create a keyboard controller object
keyboard = Controller()

# State tracking variables
last_punch_time = 0
last_jump_time = 0
is_walking = False

print(f"✅ Ready Stance Controller is running.")
print(f"Hold phone vertically, like a fist, screen facing left.")
print(f"--------------------------------------------------")
print(f"Gestures:")
print(f"  • Swing Forward/Back: Walk (Right Arrow key)")
print(f"  • Punch Forward:      Attack (X key)")
print(f"  • Jerk Upward:        Jump (Spacebar)")
print("--------------------------------------------------")

def handle_rhythmic_walking(z_value):
    """Detects a rhythmic FORWARD/BACKWARD swing and holds the 'right' arrow key."""
    global is_walking, SWING_HISTORY

    SWING_HISTORY.append(z_value)
    if len(SWING_HISTORY) < SWING_HISTORY.maxlen:
        return

    # --- Detect the start of a swing ---
    if not is_walking:
        zero_crossings = 0
        if max(SWING_HISTORY) > SWING_AMPLITUDE_THRESHOLD and min(SWING_HISTORY) < -SWING_AMPLITUDE_THRESHOLD:
            for i in range(1, len(SWING_HISTORY)):
                if (SWING_HISTORY[i-1] > 0 and SWING_HISTORY[i] < 0) or \
                   (SWING_HISTORY[i-1] < 0 and SWING_HISTORY[i] > 0):
                    zero_crossings += 1

        if zero_crossings >= SWING_CROSSING_THRESHOLD:
            print(f"SWING DETECTED! (Crossings: {zero_crossings}) -> Walking Right")
            keyboard.press(Key.right)
            is_walking = True

    # --- Detect the end of a swing ---
    else:
        if max(SWING_HISTORY) < SWING_AMPLITUDE_THRESHOLD and min(SWING_HISTORY) > -SWING_AMPLITUDE_THRESHOLD:
            print("Swing stopped. -> Halting walk.")
            keyboard.release(Key.right)
            is_walking = False
            SWING_HISTORY.clear()

# --- Main Program ---
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST_IP, PORT))

    while True:
        data, addr = s.recvfrom(1024)
        message = data.decode().strip()

        if message.startswith("SENSOR:"):
            try:
                parts = message.replace("SENSOR:", "").split(',')
                x = float(parts[0])
                y = float(parts[1])
                z = float(parts[2])
                current_time = time.time()

                # PUNCH DETECTION (strong forward thrust = negative Z)
                if z < -PUNCH_THRESHOLD and (current_time - last_punch_time) > PUNCH_COOLDOWN_S:
                    print(f"PUNCH DETECTED! (Z-axis: {z:.2f}) -> Pressing 'x'")
                    keyboard.press('x')
                    keyboard.release('x')
                    last_punch_time = current_time

                # JUMP DETECTION (strong upward jerk = positive Y)
                elif y > JUMP_THRESHOLD and (current_time - last_jump_time) > JUMP_COOLDOWN_S:
                    print(f"JUMP DETECTED! (Y-axis: {y:.2f}) -> Pressing SPACE")
                    keyboard.press('z')
                    keyboard.release('z')
                    last_jump_time = current_time

                # WALKING DETECTION (rhythmic forward/backward swing on Z axis)
                else:
                    handle_rhythmic_walking(z)

            except (ValueError, IndexError):
                pass