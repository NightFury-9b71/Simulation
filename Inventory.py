import random
import math
import matplotlib.pyplot as plt

class Inventory:
    def __init__(self):
        self.initial_inv_level = 10  # Initial inventory level (reduced to force backlog)
        self.num_values_demand = 3  # Number of demand sizes
        self.prob_distrib_demand = [0.2, 0.5, 0.3]  # Probability distribution for demand
        self.mean_interdemand = 5  # Mean interdemand time
        self.minlag, self.maxlag = 2, 5  # Lead time range (days)
        self.num_months = 12  # Total simulation months
        self.setup_cost = 100  # Cost to place an order
        self.incremental_cost = 2  # Cost per unit ordered
        self.holding_cost = 1  # Cost per unit held
        self.shortage_cost = 3  # Cost per unit short
        self.policies = [(5, 50), (8, 60)]  # Modified policies to induce backlog

    def getIIDExpo(self):
        lambda_ = 1 / self.mean_interdemand
        return random.expovariate(lambda_)

    def getIIDRandom(self):
        values = list(range(1, self.num_values_demand + 1))
        cumulative = [sum(self.prob_distrib_demand[:i+1]) for i in range(len(self.prob_distrib_demand))]
        r = random.random()
        for i, threshold in enumerate(cumulative):
            if r < threshold:
                return values[i]

    def getIIDUniform(self):
        return random.uniform(self.minlag, self.maxlag)

def simulate_policy(policy, inventory):
    smalls, bigs = policy
    clock = 1
    next_demand = int(math.ceil(inventory.getIIDExpo() * 30 * 24))
    next_supply = 0
    next_increase = 0
    backlog = 0
    sum_holding_cost = 0
    sum_ordering_cost = 0
    sum_shortest_cost = 0
    inventory_level = inventory.initial_inv_level
    
    time_series = []
    inv_series = []
    
    while clock <= inventory.num_months * 30 * 24:
        if clock % 720 == 0:  # Each month
            sum_holding_cost += inventory.holding_cost * inventory_level
            sum_shortest_cost += inventory.shortage_cost * backlog
            if inventory_level < smalls:
                next_supply = clock + int(math.ceil(inventory.getIIDUniform() * 30 * 24))
                next_increase = bigs - inventory_level
                sum_ordering_cost += inventory.setup_cost + inventory.incremental_cost * next_increase
        
        if clock == next_supply:  # Restocking event
            inventory_level += next_increase
            next_increase = 0
            if inventory_level - backlog < 0:
                backlog -= inventory_level
                inventory_level = 0
            else:
                inventory_level -= backlog
                backlog = 0
        
        if clock == next_demand:  # Demand event
            demand = inventory.getIIDRandom()
            if inventory_level - demand < 0:
                backlog += demand - inventory_level
                inventory_level = 0
            else:
                inventory_level -= demand
            next_demand = clock + int(math.ceil(inventory.getIIDExpo() * 30 * 24))
        
        time_series.append(clock)
        inv_series.append(inventory_level)
        clock += 1
    
    avg_ordering_cost = sum_ordering_cost / inventory.num_months
    avg_holding_cost = sum_holding_cost / inventory.num_months
    avg_shortest_cost = sum_shortest_cost / inventory.num_months
    total_avg_cost = avg_ordering_cost + avg_holding_cost + avg_shortest_cost
    
    return total_avg_cost, avg_ordering_cost, avg_holding_cost, avg_shortest_cost, time_series, inv_series, smalls, bigs

def main():
    inventory = Inventory()
    best_policy = None
    best_cost = float('inf')
    
    print("Policy\t\t\tAvg Total Cost\t\tAvg Ordering Cost\tAvg Holding Cost\tAvg Shortest Cost\n")
    for policy in inventory.policies:
        total_cost, ordering_cost, holding_cost, shortest_cost, time_series, inv_series, smalls, bigs = simulate_policy(policy, inventory)
        print(f"({policy[0]}, {policy[1]})\t\t\t{total_cost:.3f}\t\t\t{ordering_cost:.3f}\t\t\t{holding_cost:.3f}\t\t\t{shortest_cost:.3f}\n")
        
        if total_cost < best_cost:
            best_cost = total_cost
            best_policy = policy
            best_time_series = time_series
            best_inv_series = inv_series
            best_smalls = smalls
            best_bigs = bigs
    
    print(f"The best policy is: {best_policy}\n")
    
    plt.figure(figsize=(10, 5))
    
    # Plot the full inventory series
    plt.plot(best_time_series, best_inv_series, label=f"Inventory Level ({best_policy[0]}, {best_policy[1]})", color='blue')
    
    # Add the reorder point and max inventory lines
    plt.axhline(y=best_smalls, color='green', linestyle='dashed', label='s (Reorder Point)')
    plt.axhline(y=best_bigs, color='purple', linestyle='dashed', label='S (Max Inventory)')
    
    plt.xlabel("Time (Hours)")
    plt.ylabel("Inventory Level")
    plt.title("Inventory Level Over Time")
    plt.legend()
    plt.grid()
    plt.show()

if __name__ == "__main__":
    main()
