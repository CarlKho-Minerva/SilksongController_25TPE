import socket
import time
import json
import os

HOST_IP = '0.0.0.0'
PORT = 12345
OUTPUT_DIR = "gesture_data"

def record_action(action_name, num_samples=5, duration_s=2.5):
    """Guides the user to record multiple samples of a single action and saves the raw data to a JSON file."""
    
    print(f"\n{'='*50}")
    print(f"ACTION: {action_name.upper()}")
    print(f"{'='*50}")
    
    if action_name == "turn_around":
        print("📱 For TURN AROUND: Hold phone normally, then turn your body 180 degrees completely")
        print("   This will capture your personal turning motion signature")
    elif action_name == "walking":
        print("📱 For WALKING: Hold phone normally and walk in place naturally")
        print("   This will capture your natural walking rhythm and swing")
    elif action_name == "punch":
        print("📱 For PUNCH: Hold phone vertically, perform punching motion")
    elif action_name == "jump":
        print("📱 For JUMP: Hold phone horizontally, perform jumping motion")
        
    input(f"\nGet ready to perform '{action_name}' {num_samples} times. Press Enter to begin...")

    all_samples_data = []

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST_IP, PORT))
        s.settimeout(0.1)  # Use a timeout to avoid blocking forever

        for i in range(num_samples):
            print(f"\n  Recording sample {i+1}/{num_samples} in 3 seconds...")
            time.sleep(1)
            print("  2...")
            time.sleep(1)
            print("  1...")
            time.sleep(1)
            print("  🎬 PERFORM ACTION NOW! 🎬")

            sample_readings = []
            start_time = time.time()
            
            while time.time() - start_time < duration_s:
                try:
                    data, _ = s.recvfrom(1024)
                    message = data.decode().strip()
                    if message.startswith("SENSOR:"):
                        parts = message.replace("SENSOR:", "").split(',')
                        if len(parts) >= 4:
                            x, y, z, gyro_y = [float(p) for p in parts]
                            
                            reading = {
                                "timestamp_ms": int((time.time() - start_time) * 1000),
                                "accel_x": x,
                                "accel_y": y,
                                "accel_z": z,
                                "gyro_y": gyro_y
                            }
                            sample_readings.append(reading)

                except socket.timeout:
                    # No data received, just continue
                    continue
            
            all_samples_data.append(sample_readings)
            print(f"  ✅ Sample {i+1} complete. Recorded {len(sample_readings)} data points.")
            
            if i < num_samples - 1:
                print("  Rest for a moment before the next sample...")
                time.sleep(2)

    # Save the recorded data to a file
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    file_path = os.path.join(OUTPUT_DIR, f"{action_name.lower()}_data.json")
    with open(file_path, 'w') as f:
        json.dump(all_samples_data, f, indent=2)
        
    print(f"\n💾 Successfully saved raw data to: {file_path}")

if __name__ == "__main__":
    actions_to_record = [
        "punch",
        "jump", 
        "turn_around",  # This will capture the full 180-degree turn
        "walking"
    ]
    
    print("\n" + "="*60)
    print("🎯 INTERACTIVE GESTURE RECORDING SESSION")
    print("🎯 DATA-DRIVEN CONTROLLER CALIBRATION")
    print("="*60)
    print("\nThis tool will record YOUR unique motion patterns.")
    print("No assumptions, no guesses - just pure data from YOUR gestures.")
    print("\n📱 Make sure your Android app is running and connected!")
    
    input("\nPress Enter when ready to start recording...")

    for action in actions_to_record:
        record_action(action)

    print(f"\n{'='*60}")
    print("🎉 ALL RECORDINGS COMPLETE!")
    print(f"📂 Raw data files saved in the '{OUTPUT_DIR}/' directory:")
    print()
    for action in actions_to_record:
        print(f"   📄 {action.lower()}_data.json")
    print()
    print("🤖 You can now provide these JSON files to an AI for pattern analysis.")
    print("🧠 The AI will learn YOUR personal motion signatures and build")
    print("   a controller that feels natural and responsive to YOU.")
    print("="*60)