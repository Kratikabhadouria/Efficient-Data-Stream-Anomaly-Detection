import socket
import math
from collections import deque

class ADWIN:
    """
    ADWIN class implements the Adaptive Windowing technique for detecting concept drift
    in streaming data. This technique adjusts a sliding window size dynamically to capture 
    concept drift (change in data distribution) by compressing buckets of values.
    
    Parameters:
    - delta: Confidence parameter for detecting changes (default=0.002). Lower values make 
             the algorithm more sensitive to changes.
    """
    def __init__(self, delta=0.002):
        self.delta = delta  # Confidence parameter for detecting changes
        self.bucket_row = []  # Buckets containing recent data
        self.bucket_sizes = []  # Size of each bucket
        self.total = 0  # Running total of values in the window
        self.variance = 0  # Running variance of values in the window
        self.width = 0  # Window width (number of elements)

    def update(self, value):
        """
        Update the ADWIN model with a new value and detect changes.
        
        Parameters:
        - value (float): New data point to process.
        
        Returns:
        - (bool): Whether a change (concept drift) is detected.
        """
        self.insert_element(value)  # Insert new data point into the window
        self.compress_buckets()  # Compress adjacent buckets with the same size
        return self.detect_change()  # Check if concept drift is detected

    def insert_element(self, value):
        """
        Insert a new data element into the bucket row and update total and variance.
        """
        self.width += 1
        self.total += value
        self.variance += value * value
        self.bucket_row.append(value)
        self.bucket_sizes.append(1)  # Each new bucket starts with size 1

    def compress_buckets(self):
        """
        Compress adjacent buckets of the same size by merging them into a single bucket.
        This reduces the window size while maintaining data accuracy.
        """
        i = 0
        while i < len(self.bucket_sizes):
            k = i
            while k < len(self.bucket_sizes) and self.bucket_sizes[i] == self.bucket_sizes[k]:
                k += 1
            if k == i + 1:
                i = k  # Move to the next group of buckets
            else:
                new_bucket = sum(self.bucket_row[i:k]) / (k - i)  # Average of merged buckets
                self.bucket_row[i] = new_bucket  # Update the bucket
                self.bucket_sizes[i] *= (k - i)  # Increase bucket size
                del self.bucket_row[i+1:k]
                del self.bucket_sizes[i+1:k]  # Remove merged buckets
            i += 1

    def detect_change(self):
        """
        Detect if a change (concept drift) has occurred using the ADWIN algorithm.
        
        Returns:
        - (bool): True if a change is detected, otherwise False.
        """
        for i in range(1, len(self.bucket_sizes)):
            n0, n1 = sum(self.bucket_sizes[:i]), sum(self.bucket_sizes[i:])
            if n0 == 0 or n1 == 0:
                continue
            u0 = sum(x * y for x, y in zip(self.bucket_row[:i], self.bucket_sizes[:i])) / n0
            u1 = sum(x * y for x, y in zip(self.bucket_row[i:], self.bucket_sizes[i:])) / n1
            m = 1 / (1 / n0 + 1 / n1)
            eps = math.sqrt(2 * m * math.log(4 / self.delta) / n0 / n1)
            if abs(u0 - u1) > eps:
                # Concept drift detected, reset window
                self.width = n1
                self.total = sum(x * y for x, y in zip(self.bucket_row[i:], self.bucket_sizes[i:]))
                self.variance = sum(x * x * y for x, y in zip(self.bucket_row[i:], self.bucket_sizes[i:]))
                self.bucket_row = self.bucket_row[i:]
                self.bucket_sizes = self.bucket_sizes[i:]
                return True
        return False

class AnomalyDetector:
    """
    Anomaly Detector class using a combination of ADWIN for concept drift detection
    and Z-score for anomaly detection in streaming data.
    
    Parameters:
    - window_size: The size of the window used for Z-score anomaly detection.
    - z_threshold: Z-score threshold for flagging anomalies.
    """
    def __init__(self, window_size=50, z_threshold=3):
        self.adwin = ADWIN()  # Initialize ADWIN for concept drift detection
        self.window = deque(maxlen=window_size)  # Fixed-size window for anomaly detection
        self.z_threshold = z_threshold  # Threshold for Z-score to detect anomalies

    def detect_anomaly(self, value):
        """
        Detect anomalies using Z-score and concept drift using ADWIN.
        
        Parameters:
        - value (float): The incoming data point.
        
        Returns:
        - is_anomaly (bool): True if an anomaly is detected.
        - concept_drift (bool): True if a concept drift is detected.
        """
        self.window.append(value)  # Add the new value to the sliding window
        change_detected = self.adwin.update(value)  # Check for concept drift

        # Ensure the window is sufficiently filled before detecting anomalies
        if len(self.window) < self.window.maxlen:
            return False, change_detected

        mean = sum(self.window) / len(self.window)  # Compute the mean of the window
        variance = sum((x - mean) ** 2 for x in self.window) / len(self.window)  # Compute variance
        std_dev = math.sqrt(variance) if variance > 1e-6 else 1e-6  # Avoid division by zero

        z_score = abs((value - mean) / std_dev)  # Compute Z-score for the value
        return z_score > self.z_threshold, change_detected  # Return anomaly and concept drift status

def start_server():
    """
    Start the server to listen for incoming client connections and process
    the data stream for anomaly detection and concept drift.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket
    server_socket.bind(('localhost', 12345))  # Bind the socket to localhost and port 12345
    server_socket.listen(5)  # Listen for incoming connections (max 5)

    print("Server is waiting for connections...")
    client_socket, addr = server_socket.accept()  # Accept a connection from a client
    print(f"Connected to {addr}")

    anomaly_detector = AnomalyDetector()  # Initialize anomaly detector

    while True:
        # Receive data from the client
        data = client_socket.recv(1024).decode('utf-8')
        if not data or data == 'exit':
            print("Client has disconnected.")
            break

        try:
            data_point = float(data)  # Convert received data to a float
            print(f"Received data: {data_point}")

            # Detect anomalies and concept drift
            is_anomaly, concept_drift = anomaly_detector.detect_anomaly(data_point)

            # Send response to the client based on detection results
            if is_anomaly:
                response = f"Anomaly detected: {data_point}"
            elif concept_drift:
                response = f"Concept drift detected: {data_point}"
            else:
                response = f"Data received: {data_point}"

            client_socket.send(response.encode('utf-8'))  # Send response to client
        except ValueError:
            print(f"Invalid data received: {data}")
            client_socket.send("Invalid data".encode('utf-8'))  # Inform client of invalid data

    client_socket.close()  # Close the connection with the client
    server_socket.close()  # Close the server socket

if __name__ == "__main__":
    start_server()  # Start the server