import socket
import time
import math
import statistics

HOST_IP = "0.0.0.0"
PORT = 12345
GRAVITY_CONSTANT = 9.81  # Earth's gravity constant


def get_gesture_data(duration=3):
    """Listens for sensor data for a fixed duration and returns all readings."""
    readings = []
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST_IP, PORT))
        s.settimeout(0.1)  # Don't block forever

        print("  Recording...")
        start_time = time.time()
        while time.time() - start_time < duration:
            try:
                data, _ = s.recvfrom(1024)
                message = data.decode().strip()
                if message.startswith("SENSOR:"):
                    parts = message.replace("SENSOR:", "").split(",")
                    if len(parts) >= 4:
                        readings.append([float(p) for p in parts])
            except socket.timeout:
                continue
    print(f"  Recorded {len(readings)} data points.")
    return readings


def calibrate_punch():
    input(
        "\n--- Calibrating PUNCH (Vertical Stance) ---\nHold phone vertically. Press Enter, then perform 5 punches..."
    )
    data = get_gesture_data(10)  # 10 seconds to do 5 punches

    # CORRECTED: Calculate jerk forces, not raw accelerations
    jerk_forces = []
    for row in data:
        x, y, z = row[0], row[1], row[2]
        if abs(y) > 9.0:  # Only consider data when phone is vertical
            magnitude = math.sqrt(x**2 + y**2 + z**2)
            jerk_force = magnitude - GRAVITY_CONSTANT
            if jerk_force > 0:  # Only positive jerk forces
                jerk_forces.append(jerk_force)

    jerk_forces.sort(reverse=True)
    threshold = statistics.mean(jerk_forces[:5]) * 0.8  # Average of top 5 peaks
    print(
        f"  Raw accelerations: {[f'{abs(row[0]):.1f}' for row in data if abs(row[1]) > 9.0][:5]}"
    )
    print(f"  Jerk forces: {[f'{f:.1f}' for f in jerk_forces[:5]]}")
    print(
        f"  Calculated threshold: {threshold:.2f} (vs old method: ~{max([abs(row[0]) for row in data if abs(row[1]) > 9.0]):.1f})"
    )
    return threshold


def calibrate_jump():
    input(
        "\n--- Calibrating JUMP (Horizontal Stance) ---\nHold phone horizontally. Press Enter, then perform 5 jumps..."
    )
    data = get_gesture_data(10)

    # CORRECTED: Calculate jerk forces, not raw accelerations
    jerk_forces = []
    for row in data:
        x, y, z = row[0], row[1], row[2]
        if abs(x) > 9.0:  # Only consider vertical G-force in horizontal state
            magnitude = math.sqrt(x**2 + y**2 + z**2)
            jerk_force = magnitude - GRAVITY_CONSTANT
            if jerk_force > 0:  # Only positive jerk forces
                jerk_forces.append(jerk_force)

    jerk_forces.sort(reverse=True)
    threshold = statistics.mean(jerk_forces[:5]) * 0.8
    print(
        f"  Raw accelerations: {[f'{abs(row[0]):.1f}' for row in data if abs(row[0]) > 9.0][:5]}"
    )
    print(f"  Jerk forces: {[f'{f:.1f}' for f in jerk_forces[:5]]}")
    print(
        f"  Calculated threshold: {threshold:.2f} (vs old method: ~{max([abs(row[0]) for row in data if abs(row[0]) > 9.0]):.1f})"
    )
    return threshold


def calibrate_walk():
    input(
        "\n--- Calibrating WALK (Horizontal Stance) ---\nHold phone horizontally and walk in place. Press Enter to start..."
    )
    data = get_gesture_data(10)
    z_values = [row[2] for row in data]
    gyro_y_values = [abs(row[3]) for row in data]

    amplitude = (max(z_values) - min(z_values)) / 2
    gyro_noise = statistics.mean(gyro_y_values) * 1.5  # 150% of average noise

    return amplitude, gyro_noise


if __name__ == "__main__":
    print("✅ Full Motion Profile Calibration")
    print("Make sure your Android app is running and connected!")

    punch_thresh = calibrate_punch()
    jump_thresh = calibrate_jump()
    walk_amp, walk_gyro_noise = calibrate_walk()

    print("\n\n✅ Calibration Complete! ✅")
    print(
        "Copy the entire 'CALIBRATION_PROFILE' dictionary into your 'udp_listener.py' script:"
    )
    print("--------------------------------------------------")
    print("CALIBRATION_PROFILE = {")
    print(f"    'PUNCH_THRESHOLD': {punch_thresh:.2f},")
    print(f"    'JUMP_THRESHOLD': {jump_thresh:.2f},")
    print(f"    'WALK_SWING_AMPLITUDE': {walk_amp:.2f},")
    print(f"    'WALK_GYRO_NOISE_LIMIT': {walk_gyro_noise:.2f},")
    print("}")
    print("--------------------------------------------------")
