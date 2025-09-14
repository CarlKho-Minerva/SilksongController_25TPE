import socket
import time
import statistics
import math

HOST_IP = '0.0.0.0'
PORT = 12345
GRAVITY_CONSTANT = 9.8

def get_gesture_data(duration=10):
    """Listens for sensor data and returns all readings."""
    print("  Recording...")
    readings = []
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST_IP, PORT))
        s.settimeout(0.1)
        start_time = time.time()
        while time.time() - start_time < duration:
            try:
                data, _ = s.recvfrom(1024)
                message = data.decode().strip()
                if message.startswith("SENSOR:"):
                    parts = message.replace("SENSOR:", "").split(',')
                    if len(parts) >= 4:
                        readings.append([float(p) for p in parts])
            except socket.timeout:
                continue
    print(f"  Recorded {len(readings)} data points.")
    return readings

def calibrate_punch():
    input("\n--- Calibrating PUNCH (Vertical Stance) ---\nHold phone vertically. Press Enter, then perform 5 forward punches...")
    data = get_gesture_data()
    # A punch is a spike on the X-axis while the Y-axis feels gravity
    punch_forces = [abs(row[0]) for row in data if abs(row[1]) > (GRAVITY_CONSTANT - 2.0)]
    punch_forces.sort(reverse=True)
    # Average the top 5 distinct force readings
    threshold = statistics.mean(punch_forces[:5]) * 0.8
    return threshold

def calibrate_jump():
    input("\n--- Calibrating JUMP (Horizontal Stance) ---\nHold phone horizontally. Press Enter, then perform 5 upward jerks...")
    data = get_gesture_data()
    # A jump is a spike on the X-axis, which is already feeling gravity. We want the force ADDED to gravity.
    # We calculate the magnitude of the force vector and subtract gravity to find the jerk force.
    jump_forces = []
    for row in data:
        # Only measure when in a clear horizontal state
        if abs(row[0]) > (GRAVITY_CONSTANT - 2.0):
            magnitude = math.sqrt(row[0]**2 + row[1]**2 + row[2]**2)
            jerk_force = magnitude - GRAVITY_CONSTANT
            if jerk_force > 0:
                jump_forces.append(jerk_force)

    jump_forces.sort(reverse=True)
    threshold = statistics.mean(jump_forces[:5]) * 0.8 if len(jump_forces) >= 5 else 10.0
    return threshold

if __name__ == "__main__":
    print("✅ Full Motion Profile Calibration")
    punch_thresh = calibrate_punch()
    jump_thresh = calibrate_jump()

    print("\n\n✅ Calibration Complete! ✅")
    print("Copy the following configuration into your 'udp_listener.py' script:")
    print("--------------------------------------------------")
    print(f"PUNCH_THRESHOLD = {punch_thresh:.2f}")
    print(f"JUMP_THRESHOLD = {jump_thresh:.2f}")
    print("--------------------------------------------------")