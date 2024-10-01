# Efficient-Data-Stream-Anomaly-Detection
# Project Overview
This project demonstrates an anomaly detection system that simulates continuous data streams, detects anomalies in real time, and visualizes the results. The data stream can represent metrics such as financial transactions or system measurements, and the system uses the ADWIN algorithm for detecting concept drift and Z-score analysis for anomaly detection.
# Key Features:
Simulated Data Stream: Data includes regular patterns, seasonal fluctuations, and occasional anomalies.
Anomaly Detection: Combines ADWIN for detecting concept drift and Z-score for identifying anomalies.
Real-Time Visualization: Continuously plots the data stream and marks detected anomalies in real-time.
# Project Structure
simulate_data.py: Simulates real-time sensor data with regular patterns, seasonal variations, and random noise. It occasionally introduces anomalies and sends the data to the server.
server.py: Processes the incoming data using the ADWIN algorithm to detect concept drift and Z-score anomaly detection. It sends appropriate feedback to the client.
visualize.py: Plots the real-time data stream, highlighting anomalies with red dots.
