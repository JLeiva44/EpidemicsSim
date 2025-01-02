class SimulationAnalyzer:
    def __init__(self):
        """
        Initialize the simulation analyzer.
        """
        self.daily_stats = []

    def record_daily_stats(self, agents):
        """
        Record statistics for the current day.

        :param agents: List of agents in the simulation.
        """
        stats = {
            "susceptible": sum(1 for agent in agents if agent.state == "susceptible"),
            "infected": sum(1 for agent in agents if agent.state == "infected"),
            "recovered": sum(1 for agent in agents if agent.state == "recovered"),
            "immune": sum(1 for agent in agents if agent.state == "immune"),
        }
        self.daily_stats.append(stats)

    def generate_report(self):
        """
        Generate a summary report of the simulation.

        :return: A dictionary containing cumulative statistics.
        """
        report = {
            "total_days": len(self.daily_stats),
            "total_susceptible": sum(day["susceptible"] for day in self.daily_stats),
            "total_infected": sum(day["infected"] for day in self.daily_stats),
            "total_recovered": sum(day["recovered"] for day in self.daily_stats),
            "total_immune": sum(day["immune"] for day in self.daily_stats),
        }
        return report

    def plot_statistics(self):
        """
        Plot the daily statistics using matplotlib.
        """
        import matplotlib.pyplot as plt

        days = range(1, len(self.daily_stats) + 1)
        susceptible = [day["susceptible"] for day in self.daily_stats]
        infected = [day["infected"] for day in self.daily_stats]
        recovered = [day["recovered"] for day in self.daily_stats]
        immune = [day["immune"] for day in self.daily_stats]

        plt.figure(figsize=(10, 6))
        plt.plot(days, susceptible, label="Susceptible")
        plt.plot(days, infected, label="Infected")
        plt.plot(days, recovered, label="Recovered")
        plt.plot(days, immune, label="Immune")
        plt.xlabel("Day")
        plt.ylabel("Number of Agents")
        plt.title("Disease Progression Over Time")
        plt.legend()
        plt.grid()
        plt.show()

# Example usage of SimulationAnalyzer
if __name__ == "__main__":
    class MockAgent:
        def __init__(self, state):
            self.state = state

    # Mock simulation
    agents = [MockAgent(state="susceptible") for _ in range(70)] + \
             [MockAgent(state="infected") for _ in range(20)] + \
             [MockAgent(state="recovered") for _ in range(10)]

    analyzer = SimulationAnalyzer()

    # Simulate recording stats for 5 days
    for _ in range(5):
        analyzer.record_daily_stats(agents)
        # Mock state changes (just for testing)
        for agent in agents:
            if agent.state == "infected":
                agent.state = "recovered"

    # Generate report and plot
    report = analyzer.generate_report()
    print("Simulation Report:", report)
    analyzer.plot_statistics()
