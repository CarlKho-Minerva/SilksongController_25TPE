import socket

# --- Configuration ---
# Use '0.0.0.0' to listen on all available network interfaces on your Mac.
# This is more robust than using a specific IP.
HOST_IP = '0.0.0.0'

# This port MUST match the TARGET_PORT in your Android app.
PORT = 12345
# ---------------------

# Create a UDP socket.
# AF_INET specifies we're using the IPv4 protocol.
# SOCK_DGRAM specifies that it's a UDP socket.
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    # Bind the socket to the host and port, making it a server.
    s.bind((HOST_IP, PORT))

    print(f"✅ Python listener is running.")
    print(f"Listening for controller data on port {PORT}...")
    print("--------------------------------------------------")
    print("Start the app on your phone to see data stream.")

    # Loop forever to continuously listen for data.
    while True:
        # Wait here until a packet is received.
        # 1024 is the buffer size (how much data to read at once).
        data, addr = s.recvfrom(1024)

        # Decode the received bytes into a human-readable string
        # and print it to the terminal.
        command = data.decode().strip()
        print(f"Received from {addr}: {command}")
