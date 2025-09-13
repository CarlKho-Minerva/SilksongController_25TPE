import socket
import time
import statistics

HOST_IP = '0.0.0.0'
PORT = 12345

def record_gesture(gesture_name, num_samples=5):
    """Guides the user to record a gesture and finds the average peak value."""
    print(f"\n--- Calibrating: {gesture_name} ---")
    input(f"Get ready to perform '{gesture_name}' {num_samples} times. Press Enter to start...")
    
    samples = []
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST_IP, PORT))
        
        for i in range(num_samples):
            print(f"  Recording sample {i+1}/{num_samples}... Perform the gesture NOW.")
            
            peak_x = 0
            peak_y = 0

            start_time = time.time()
            while time.time() - start_time < 2: # Record for 2 seconds
                try:
                    data, _ = s.recvfrom(1024)
                    message = data.decode().strip()
                    if message.startswith("SENSOR:"):
                        parts = message.replace("SENSOR:", "").split(',')
                        if len(parts) >= 3:  # Handle both 3 and 4 value formats
                            x = float(parts[0])
                            y = float(parts[1])
                            if abs(x) > peak_x: peak_x = abs(x)
                            if abs(y) > peak_y: peak_y = abs(y)
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"  Error reading data: {e}")
                    continue
            
            if gesture_name == "PUNCH":
                samples.append(peak_x)
                print(f"  Peak X-Force recorded: {peak_x:.2f}")
            elif gesture_name == "JUMP":
                samples.append(peak_y)
                print(f"  Peak Y-Force recorded: {peak_y:.2f}")

            time.sleep(1) # Cooldown between samples

    # Calculate 80% of the average value for a reliable threshold
    if samples:
        avg_value = statistics.mean(samples)
        threshold = avg_value * 0.8
        print(f"--- Calibration for {gesture_name} complete! ---")
        return threshold
    else:
        print(f"--- No data recorded for {gesture_name}! ---")
        return 5.0 if gesture_name == "PUNCH" else 15.0  # Default values

if __name__ == "__main__":
    print("✅ Gesture Calibration Script")
    print("="*50)
    print("This script will help you calibrate your personal gesture thresholds.")
    print("Make sure your Android app is running and connected!")
    print("="*50)
    
    try:
        punch_threshold = record_gesture("PUNCH")
        jump_threshold = record_gesture("JUMP")

        print("\n\n✅ Calibration Complete! ✅")
        print("Copy the following lines into your 'udp_listener.py' script:")
        print("--------------------------------------------------")
        print(f"PUNCH_THRESHOLD = {punch_threshold:.2f}")
        print(f"JUMP_THRESHOLD = {jump_threshold:.2f}")
        print("--------------------------------------------------")
        print("\nInstructions:")
        print("1. Copy the lines above")
        print("2. Open udp_listener.py")
        print("3. Replace the existing PUNCH_THRESHOLD and JUMP_THRESHOLD values")
        print("4. Save the file and run the controller!")
        
    except KeyboardInterrupt:
        print("\n\nCalibration cancelled by user.")
    except Exception as e:
        print(f"\nError during calibration: {e}")