#!/usr/bin/env python3
"""
Quick test script to verify UDP communication format.
Run this instead of udp_listener.py to test the Android app transmission.
"""

import socket

HOST_IP = '0.0.0.0'
PORT = 12345

print("🔧 UDP Protocol Test")
print("=" * 50)
print("This script will show exactly what data the Android app sends.")
print("Start the Android app and connect to this machine's IP address.")
print("Press Ctrl+C to stop.")
print()

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST_IP, PORT))
    print(f"📡 Listening on {HOST_IP}:{PORT}")
    print()

    packet_count = 0
    try:
        while True:
            data, addr = s.recvfrom(1024)
            message = data.decode().strip()
            packet_count += 1

            print(f"Packet #{packet_count} from {addr[0]}:")
            print(f"  Raw message: {message}")

            if message.startswith("SENSOR:"):
                try:
                    parts = message.replace("SENSOR:", "").split(',')
                    print(f"  Number of values: {len(parts)}")
                    print(f"  Values: {parts}")

                    if len(parts) == 4:
                        x, y, z, gyro_y = [float(p) for p in parts]
                        print(f"  ✅ CORRECT FORMAT: x={x:.2f}, y={y:.2f}, z={z:.2f}, gyro_y={gyro_y:.2f}")
                    else:
                        print(f"  ❌ WRONG FORMAT: Expected 4 values, got {len(parts)}")

                except Exception as e:
                    print(f"  ❌ PARSE ERROR: {e}")
            else:
                print(f"  ❌ INVALID FORMAT: Message doesn't start with 'SENSOR:'")

            print("-" * 50)

    except KeyboardInterrupt:
        print("\n\n🛑 Test stopped by user")
        print(f"📊 Total packets received: {packet_count}")