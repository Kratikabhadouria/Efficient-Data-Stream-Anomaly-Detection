# simulate_data.py

import socket
import random
import time
import threading
import queue
import math

data_queue = queue.Queue()

def simulate_data(t):
    """
    Simulates sensor data with regular patterns, seasonal elements, random noise,
    and occasional anomalies.
    
    Parameters:
    - t: time step (int)
    
    Returns:
    - value (float): The simulated sensor data.
    - is_anomaly (bool): Whether the data is an anomaly.
    """
    # Regular pattern: simulate daily cycles (e.g., temperature)
    regular_pattern = 50 + 10 * math.sin(2 * math.pi * t / 24)
    
    # Seasonal pattern: simulate yearly cycles (e.g., energy consumption)
    seasonal_pattern = 10 * math.sin(2 * math.pi * t / 365)
    
    # Random noise
    noise = random.uniform(-2, 2)
    
    # Occasionally introduce anomalies
    if random.random() < 0.05:  # 5% chance of anomaly
        anomaly_value = regular_pattern + seasonal_pattern + noise + random.uniform(30, 40)
        return anomaly_value, True
    
    return regular_pattern + seasonal_pattern + noise, False

def start_client():
    """
    Function to start the client that sends simulated data to the server.
    It continuously sends the simulated data to the server and receives responses.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 12345))  # Connect to the server

    try:
        t = 0  # Initialize time step
        while True:
            # Simulate data and send to server
            floating_data, is_anomaly = simulate_data(t)
            print(f"Sending: {floating_data}")
            client_socket.send(str(floating_data).encode('utf-8'))

            # Receive server response
            response = client_socket.recv(1024).decode('utf-8')
            print(f"Received from server: {response}")

            # Add data to queue for visualization
            if "Anomaly detected" in response:
                anomaly_value = float(response.split(": ")[1])
                data_queue.put((anomaly_value, True))
            else:
                normal_value = float(response.split(": ")[1])
                data_queue.put((normal_value, False))

            t += 1
            time.sleep(0.3)  # Reduced sleep time for faster data generation
    except KeyboardInterrupt:
        print("Disconnecting from server...")
        client_socket.send('exit'.encode('utf-8'))

    client_socket.close()

# Start the client in a separate thread
threading.Thread(target=start_client, daemon=True).start()