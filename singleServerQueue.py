import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
from random import uniform


class QueueSimulation:
    def __init__(self, num_customers=30, interval=5, service_time_range=(5, 7)):

        self.num_customers = num_customers
        self.interval = interval
        self.service_time_range = service_time_range
        
        self.queue = []
        self.service_queue = []
        self.completed_customers = []
        self.current_time = 0
        self.served_customers = 0
        self.total_queue_time = 0 
        self.total_waiting_time = 0  # Variable to accumulate total waiting time
        self.customers = []
        self.queue_length_history = []  # To store the queue length over time
        self.time_history = []  # To store the actual time for each queue length entry
        
        # Generate customers
        self.generate_customers()
        
        # Setup plot
        self.fig, (self.ax, self.ax_queue) = plt.subplots(1, 2, figsize=(16, 6))

    def generate_customers(self):

        arrival_times = [uniform(c * self.interval, (c + 1) * self.interval) for c in range(self.num_customers)]
        service_times = [uniform(*self.service_time_range) for _ in range(self.num_customers)]

        self.customers = [
            {'id': i, 'arrival_time': at, 'service_time': st, 'status': 'waiting', 'pos_x': 0, 'pos_y': 2.5}
            for i, (at, st) in enumerate(zip(arrival_times, service_times))
        ]

    def setup_plot(self):

        self.ax.clear()
        self.ax.set_xlim(0, 12)
        self.ax.set_ylim(0, 6)
        
        # Queue Box
        queue_box = patches.Rectangle((1, 1), 3, 4, fill=False, edgecolor='red')
        self.ax.add_patch(queue_box)
        self.ax.text(2.5, 5.5, f'Queue Box: {len(self.queue)}', ha='center', fontweight='bold')
        
        # Service Box
        service_box = patches.Rectangle((7, 1), 3, 4, fill=False, edgecolor='green')
        self.ax.add_patch(service_box)
        self.ax.text(8.5, 5.5, f'Service Box: {self.served_customers}/{self.num_customers}', ha='center', fontweight='bold')
        

        # Display time
        self.ax.text(6, 0.5, f'Time: {self.current_time:.2f}', ha='center')

        # Average Queue Length
        self.avg_queue_len = self.total_queue_time / self.current_time if self.current_time > 0 else 0
        # Average Waiting Time
        avg_waiting_time = self.total_waiting_time / self.served_customers if self.served_customers > 0 else 0
        
        self.ax.set_title(f'Avg Queue Length: {self.avg_queue_len:.2f}\nAvg Waiting Time: {avg_waiting_time:.2f}', ha='center')

    def process_customers(self):

        # Add new arrivals to queue
        for customer in self.customers[:]:
            if customer['arrival_time'] <= self.current_time and customer['status'] == 'waiting':
                self.queue.append(customer)
                customer['status'] = 'in_queue'
                self.customers.remove(customer)

        # Update total queue time
        self.total_queue_time += len(self.queue) * 0.05  # Small time slice (frame time)
        
        # Move customers from queue to service
        if not self.service_queue and self.queue:
            customer = self.queue.pop(0)
            customer['status'] = 'moving_to_service'
            customer['service_start_time'] = self.current_time
            self.service_queue.append(customer)

        # Handle customers in service
        for customer in self.service_queue[:]:
            if customer['status'] == 'moving_to_service':
                customer['pos_x'] += 0.2
                if customer['pos_x'] >= 7.5:
                    customer['status'] = 'in_service'
            
            if customer['status'] == 'in_service':
                if self.current_time >= customer['service_start_time'] + customer['service_time']:
                    # Calculate waiting time for this customer and accumulate it
                    waiting_time = (self.current_time - customer['arrival_time'] - customer['service_time'])
                    self.total_waiting_time += waiting_time
                    
                    customer['status'] = 'completed'
                    self.service_queue.remove(customer)
                    self.completed_customers.append(customer)
                    self.served_customers += 1

    def visualize_customers(self):

        # Customers in queue
        for i, customer in enumerate(self.queue):
            customer['pos_x'] = 1.5  
            customer['pos_y'] = 2.5 + i * 0.3 
            self.ax.plot(customer['pos_x'], customer['pos_y'], 'bo', markersize=8)
        
        # Customers in service or moving to service
        for customer in self.service_queue:
            color = 'ro' if customer['status'] == 'in_service' else 'bo'
            self.ax.plot(customer['pos_x'], customer['pos_y'], color, markersize=8)

        # Completed customers leaving
        for customer in self.completed_customers:
            customer['pos_x'] += 0.2
            self.ax.plot(customer['pos_x'], customer['pos_y'], 'go', markersize=8) 

    def update_queue_graph(self):

        # Add current time and queue length to history
        self.queue_length_history.append(len(self.queue))
        self.time_history.append(self.current_time)

        # Update the queue length graph
        self.ax_queue.clear()
        self.ax_queue.plot(self.time_history, self.queue_length_history, color='b', label="Queue Length")
        self.ax_queue.set_title("Queue Length Over Time")
        self.ax_queue.set_xlabel("Time")
        self.ax_queue.set_ylabel("Queue Length")
        self.ax_queue.legend(loc="upper right")

    def animate(self, frame):

        self.current_time += 0.05  # Increment simulation time
        
        self.process_customers()
        self.setup_plot()
        self.visualize_customers()
        self.update_queue_graph()
        
        # End simulation when all customers are served
        if self.served_customers >= self.num_customers:
            print("All customers served.")
            print(f"Average Queue length = {self.avg_queue_len}")
            print(f"Average Waiting Time = {self.total_waiting_time / self.served_customers:.2f}")
            plt.close(self.fig)

    def run_simulation(self):
        anim = animation.FuncAnimation(
            self.fig,
            self.animate,
            interval=50,  # Animation speed (ms per frame)
            blit=False,
        )
        plt.show()


# Run the simulation
if __name__ == '__main__':
    sim = QueueSimulation()
    sim.run_simulation()
