import socket
import time
import math
import statistics

HOST_IP = '0.0.0.0'
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
                    parts = message.replace("SENSOR:", "").split(',')

                    # HANDLE NEW COMPREHENSIVE DATA FORMAT (12 values)
                    if len(parts) == 12:
                        # Parse all 12 sensor values for comprehensive analysis
                        sensor_data = {
                            'accel_x': float(parts[0]),
                            'accel_y': float(parts[1]),
                            'accel_z': float(parts[2]),
                            'gyro_x': float(parts[3]),
                            'gyro_y': float(parts[4]),
                            'gyro_z': float(parts[5]),
                            'linear_accel_x': float(parts[6]),
                            'linear_accel_y': float(parts[7]),
                            'linear_accel_z': float(parts[8]),
                            'gravity_x': float(parts[9]),
                            'gravity_y': float(parts[10]),
                            'gravity_z': float(parts[11])
                        }
                        readings.append(sensor_data)
                    elif len(parts) >= 4:
                        # LEGACY FORMAT: maintain backward compatibility
                        legacy_data = {
                            'accel_x': float(parts[0]),
                            'accel_y': float(parts[1]),
                            'accel_z': float(parts[2]),
                            'gyro_y': float(parts[3]),
                            'gyro_x': 0.0, 'gyro_z': 0.0,
                            'linear_accel_x': 0.0, 'linear_accel_y': 0.0, 'linear_accel_z': 0.0,
                            'gravity_x': 0.0, 'gravity_y': 0.0, 'gravity_z': 0.0
                        }
                        readings.append(legacy_data)
            except socket.timeout:
                continue
    print(f"  Recorded {len(readings)} data points.")
    return readings

def calibrate_punch():
    input("\n--- Calibrating PUNCH (Vertical Stance) ---\n"
          "Hold phone vertically. Press Enter, then perform 5 punches...")
    data = get_gesture_data(10)  # 10 seconds to do 5 punches

    # CORRECTED: Calculate jerk forces, not raw accelerations
    jerk_forces = []
    for row in data:
        x, y, z = row['accel_x'], row['accel_y'], row['accel_z']
        if abs(y) > 9.0:  # Only consider data when phone is vertical
            magnitude = math.sqrt(x**2 + y**2 + z**2)
            jerk_force = magnitude - GRAVITY_CONSTANT
            if jerk_force > 0:  # Only positive jerk forces
                jerk_forces.append(jerk_force)

    jerk_forces.sort(reverse=True)
    # Average of top 5 peaks
    threshold = statistics.mean(jerk_forces[:5]) * 0.8
    vertical_rows = [row for row in data if abs(row['accel_y']) > 9.0]
    raw_accels = [f"{abs(row['accel_x']):.1f}" for row in vertical_rows[:5]]
    max_accel = max([abs(row['accel_x']) for row in vertical_rows])

    print(f"  Raw accelerations: {raw_accels}")
    print(f"  Jerk forces: {[f'{f:.1f}' for f in jerk_forces[:5]]}")
    print(f"  Calculated threshold: {threshold:.2f} "
          f"(vs old method: ~{max_accel:.1f})")
    return threshold


def calibrate_jump():
    input("\n--- Calibrating JUMP (Horizontal Stance) ---\n"
          "Hold phone horizontally. Press Enter, then perform 5 jumps...")
    data = get_gesture_data(10)

    # CORRECTED: Calculate jerk forces, not raw accelerations
    jerk_forces = []
    for row in data:
        x, y, z = row['accel_x'], row['accel_y'], row['accel_z']
        if abs(x) > 9.0:  # Only consider vertical G-force in horizontal state
            magnitude = math.sqrt(x**2 + y**2 + z**2)
            jerk_force = magnitude - GRAVITY_CONSTANT
            if jerk_force > 0:  # Only positive jerk forces
                jerk_forces.append(jerk_force)

    jerk_forces.sort(reverse=True)
    threshold = statistics.mean(jerk_forces[:5]) * 0.8
    horizontal_rows = [row for row in data if abs(row['accel_x']) > 9.0]
    raw_accels = [f"{abs(row['accel_x']):.1f}" for row in horizontal_rows[:5]]
    max_accel = max([abs(row['accel_x']) for row in horizontal_rows])

    print(f"  Raw accelerations: {raw_accels}")
    print(f"  Jerk forces: {[f'{f:.1f}' for f in jerk_forces[:5]]}")
    print(f"  Calculated threshold: {threshold:.2f} "
          f"(vs old method: ~{max_accel:.1f})")
    return threshold


def calibrate_walk():
    input("\n--- Calibrating WALK (Horizontal Stance) ---\n"
          "Hold phone horizontally and walk in place. "
          "Press Enter to start...")
    data = get_gesture_data(10)
    z_values = [row['accel_z'] for row in data]
    gyro_y_values = [abs(row['gyro_y']) for row in data]

    amplitude = (max(z_values) - min(z_values)) / 2
    gyro_noise = statistics.mean(gyro_y_values) * 1.5  # 150% of average noise

    return amplitude, gyro_noise


def calibrate_turn_left():
    """NEW: Comprehensive turn left data collection"""
    input("\n--- Calibrating TURN LEFT (180° rotation) ---\n"
          "Hold phone horizontally. Press Enter, then slowly turn around "
          "180° to the LEFT...")
    data = get_gesture_data(8)  # 8 seconds for slow turn

    print("  📊 LEFT TURN DATA ANALYSIS:")
    print(f"    Total data points: {len(data)}")
    if data:
        gyro_data = [row['gyro_y'] for row in data]
        linear_accel_data = [row['linear_accel_y'] for row in data]
        print(f"    Gyro Y range: {min(gyro_data):.3f} to {max(gyro_data):.3f}")
        print(f"    Linear accel Y range: {min(linear_accel_data):.3f} to "
              f"{max(linear_accel_data):.3f}")
    return data


def calibrate_turn_right():
    """NEW: Comprehensive turn right data collection"""
    input("\n--- Calibrating TURN RIGHT (180° rotation) ---\n"
          "Hold phone horizontally. Press Enter, then slowly turn around "
          "180° to the RIGHT...")
    data = get_gesture_data(8)  # 8 seconds for slow turn

    print("  📊 RIGHT TURN DATA ANALYSIS:")
    print(f"    Total data points: {len(data)}")
    if data:
        gyro_data = [row['gyro_y'] for row in data]
        linear_accel_data = [row['linear_accel_y'] for row in data]
        print(f"    Gyro Y range: {min(gyro_data):.3f} to {max(gyro_data):.3f}")
        print(f"    Linear accel Y range: {min(linear_accel_data):.3f} to "
              f"{max(linear_accel_data):.3f}")
    return data


if __name__ == "__main__":
    print("✅ Full Motion Profile Calibration - ENHANCED DATA COLLECTION")
    print("Make sure your Android app is running and connected!")

    punch_thresh = calibrate_punch()
    jump_thresh = calibrate_jump()
    walk_amp, walk_gyro_noise = calibrate_walk()

    # NEW: Comprehensive turn data collection for empirical analysis
    print("\n🔄 TURN PATTERN DATA COLLECTION")
    left_turn_data = calibrate_turn_left()
    right_turn_data = calibrate_turn_right()

    print("\n\n✅ Calibration Complete! ✅")
    print("Copy the entire 'CALIBRATION_PROFILE' dictionary into your "
          "'udp_listener.py' script:")
    print("--------------------------------------------------")
    print("CALIBRATION_PROFILE = {")
    print(f"    'PUNCH_THRESHOLD': {punch_thresh:.2f},")
    print(f"    'JUMP_THRESHOLD': {jump_thresh:.2f},")
    print(f"    'WALK_SWING_AMPLITUDE': {walk_amp:.2f},")
    print(f"    'WALK_GYRO_NOISE_LIMIT': {walk_gyro_noise:.2f},")
    print("}")
    print("--------------------------------------------------")
    print(f"\n📊 COLLECTED COMPREHENSIVE SENSOR DATA:")
    print(f"  Left turn samples: {len(left_turn_data)}")
    print(f"  Right turn samples: {len(right_turn_data)}")
    print("  This data can be used for advanced motion pattern analysis!")