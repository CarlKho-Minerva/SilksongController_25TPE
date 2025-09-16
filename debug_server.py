#!/usr/bin/env python3
"""
Simple UDP test server to debug Android app connectivity.
Run this script and use your computer's IP address in the Android app.
"""

import socket
import time

def run_test_server():
    HOST_IP = '0.0.0.0'
    PORT = 12345
    
    print(f"Starting UDP test server on port {PORT}")
    print("Use your computer's IP address in the Android app to connect.")
    print("Press Ctrl+C to stop the server.\n")
    
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST_IP, PORT))
        s.settimeout(1.0)  # 1 second timeout
        
        packet_count = 0
        last_update = time.time()
        
        while True:
            try:
                data, addr = s.recvfrom(1024)
                message = data.decode().strip()
                packet_count += 1
                
                current_time = time.time()
                if current_time - last_update >= 2.0:  # Update every 2 seconds
                    print(f"📡 Received {packet_count} packets from {addr[0]}")
                    
                    if message.startswith("SENSOR:"):
                        parts = message.replace("SENSOR:", "").split(',')
                        if len(parts) >= 12:
                            print(f"✅ Valid sensor data with {len(parts)} values")
                            print(f"   Accel: {parts[0]}, {parts[1]}, {parts[2]}")
                            print(f"   Gyro:  {parts[3]}, {parts[4]}, {parts[5]}")
                            print(f"   LinearAccel: {parts[6]}, {parts[7]}, {parts[8]}")
                            print(f"   Gravity: {parts[9]}, {parts[10]}, {parts[11]}")
                        else:
                            print(f"❌ Invalid sensor data - only {len(parts)} values")
                    else:
                        print(f"📄 Raw message: {message[:100]}...")
                    
                    print("-" * 50)
                    last_update = current_time
                    
            except socket.timeout:
                continue
            except KeyboardInterrupt:
                print("\n🛑 Server stopped by user")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_test_server()