import socket
import time
import json
import os

HOST_IP = '0.0.0.0'
PORT = 12345
OUTPUT_DIR = "gesture_data"


def record_action(action_name, num_samples=3, duration_s=2.5):
    """Records multiple samples of an action and saves raw data to JSON."""

    print(f"\n{'='*50}")
    print(f"ACTION: {action_name.upper()}")
    print(f"{'='*50}")
    input(f"Get ready to perform '{action_name}' {num_samples} times. "
          f"Press Enter to begin...")

    all_samples_data = []

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST_IP, PORT))
        s.settimeout(0.1)

        for i in range(num_samples):
            print(f"\n  Recording sample {i+1}/{num_samples} in 3 seconds...")
            time.sleep(3)
            print("  ... PERFORM ACTION NOW ...")

            sample_readings = []
            start_time = time.time()

            while time.time() - start_time < duration_s:
                try:
                    data, _ = s.recvfrom(1024)
                    message = data.decode().strip()
                    if message.startswith("SENSOR:"):
                        parts = message.replace("SENSOR:", "").split(',')
                        # Check for the new comprehensive format
                        if len(parts) >= 12:
                            readings = [float(p) for p in parts]

                            data_point = {
                                "timestamp_ms": int(
                                    (time.time() - start_time) * 1000),
                                "accel": {
                                    "x": readings[0],
                                    "y": readings[1],
                                    "z": readings[2]
                                },
                                "gyro": {
                                    "x": readings[3],
                                    "y": readings[4],
                                    "z": readings[5]
                                },
                                "linear_accel": {
                                    "x": readings[6],
                                    "y": readings[7],
                                    "z": readings[8]
                                },
                                "gravity": {
                                    "x": readings[9],
                                    "y": readings[10],
                                    "z": readings[11]
                                }
                            }
                            sample_readings.append(data_point)

                except socket.timeout:
                    continue

            all_samples_data.append(sample_readings)
            print(f"  Sample {i+1} complete. "
                  f"Recorded {len(sample_readings)} data points.")

    # Save the recorded data to a file
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    file_path = os.path.join(OUTPUT_DIR, f"{action_name.lower()}_data.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(all_samples_data, f, indent=2)

    print(f"\n✅ Successfully saved raw data to: {file_path}")


if __name__ == "__main__":
    actions_to_record = [
        "punch",
        "jump",
        "turn_right",
        "turn_left",
        "walking"
    ]

    print("\nStarting Comprehensive Gesture Recording Session.")
    print("This will record your raw sensor data, including all gyroscope "
          "axes and specialized sensors.")

    for action in actions_to_record:
        record_action(action)

    print(f"\n{'='*50}")
    print("✅ All recordings complete!")
    print(f"The raw data files are saved in the '{OUTPUT_DIR}/' directory.")
    print("Provide the contents of these JSON files to the AI for pattern "
          "analysis.")
    print("="*50)