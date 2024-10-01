import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import simulate_data  # Import the client module to access the data queue

# Data structure to store the data stream and anomaly points
data_stream = []  # Stores the data stream values
anomalies = []  # Stores positions of anomalies (None if no anomaly)

# Explanation of the chosen algorithm:
# This algorithm fetches real-time data points from a simulated data queue and appends them to the data stream.
# It checks if the current data point is an anomaly. If it is, the anomaly is marked and plotted on the graph.
# Anomalies are highlighted using red scatter points to clearly identify them in the data stream plot.
# This real-time visualization is useful in identifying patterns or unusual behaviors in the data as they occur.

# Function to update the plot with real-time data
def update(frame):
    # Retrieve data points from the data queue (simulated real-time stream)
    while not simulate_data.data_queue.empty():
        data_point, is_anomaly = simulate_data.data_queue.get()  # Get the latest data point and anomaly flag
        data_stream.append(data_point)  # Append new data to the stream
        anomalies.append(data_point if is_anomaly else None)  # Mark anomaly position if detected

    # Clear the current plot before redrawing
    ax.clear()
    
    # Plot the real-time data stream
    ax.plot(data_stream, label='Data Stream', color='blue')
    
    # Highlight anomalies with red scatter points
    if anomalies:
        anomaly_indices = [i for i, val in enumerate(anomalies) if val is not None]  # Indices of anomalies
        anomaly_values = [val for val in anomalies if val is not None]  # Values of anomalies
        ax.scatter(anomaly_indices, anomaly_values, color='red', label='Anomalies')  # Plot anomalies

    # Set plot labels and legend
    ax.legend(loc='upper left')
    ax.set_title('Real-time Data Stream with Anomaly Detection')
    ax.set_xlabel('Time')
    ax.set_ylabel('Value')

# Function to visualize the data in real-time
def visualize_data():
    global fig, ax
    fig, ax = plt.subplots()  # Create a figure and axis for plotting
    ani = FuncAnimation(fig, update, interval=1000)  # Update the plot every second
    plt.show()  # Display the plot window

# Main execution starts here
if __name__ == "__main__":
    visualize_data()  # Call the function to start visualizing real-time data