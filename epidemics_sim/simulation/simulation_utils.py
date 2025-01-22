import matplotlib.pyplot as plt

class SimulationAnalyzer:
    def __init__(self):
        """
        Initialize the simulation analyzer.
        """
        self.daily_stats = []

    def record_daily_stats(self, agents):
        """
        Record statistics for the current day, focusing on the disease progression.

        :param agents: List of agents in the simulation.
        """
        stats = {
            "susceptible": sum(1 for agent in agents if agent.infection_status["state"] == "susceptible"),
            "infected": sum(1 for agent in agents if agent.infection_status["state"] == "infected"),
            "recovered": sum(1 for agent in agents if agent.infection_status["state"] == "recovered"),
            "immune": sum(1 for agent in agents if agent.immune),
            "deceased": sum(1 for agent in agents if agent.infection_status["state"] == "deceased"),
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
            "total_deceased": sum(day["deceased"] for day in self.daily_stats),
        }
        return report

    def plot_disease_progression(self):
        """
        Plot the daily statistics related to disease progression using matplotlib.
        """
        days = range(1, len(self.daily_stats) + 1)
        susceptible = [day["susceptible"] for day in self.daily_stats]
        infected = [day["infected"] for day in self.daily_stats]
        recovered = [day["recovered"] for day in self.daily_stats]
        immune = [day["immune"] for day in self.daily_stats]
        deceased = [day["deceased"] for day in self.daily_stats]

        plt.figure(figsize=(10, 6))

        plt.plot(days, susceptible, label="Susceptible", color="blue")
        plt.plot(days, infected, label="Infected", color="red")
        plt.plot(days, recovered, label="Recovered", color="green")
        plt.plot(days, immune, label="Immune", color="purple")
        plt.plot(days, deceased, label="Deceased", linestyle="--", color="black")

        plt.title("Disease Progression Over Time")
        plt.xlabel("Day")
        plt.ylabel("Number of Agents")
        plt.legend()
        plt.grid()

        plt.tight_layout()
        plt.show()

# Example usage
if __name__ == "__main__":
    class Agent:
        """
        Mock Agent class for testing purposes.
        """
        def __init__(self, state, immune=False):
            self.infection_status = {"state": state}
            self.immune = immune

    # Example agents
    agents = (
        [Agent("susceptible") for _ in range(500)] +
        [Agent("infected") for _ in range(100)] +
        [Agent("recovered", immune=True) for _ in range(50)] +
        [Agent("deceased") for _ in range(10)]
    )

    analyzer = SimulationAnalyzer()

    # Simulate daily stats recording
    for day in range(10):
        # Randomly change states for testing (mock progression)
        for agent in agents:
            if agent.infection_status["state"] == "infected" and random.random() < 0.2:
                agent.infection_status["state"] = "recovered"
                agent.immune = True
            elif agent.infection_status["state"] == "susceptible" and random.random() < 0.1:
                agent.infection_status["state"] = "infected"

        analyzer.record_daily_stats(agents)

    # Generate report and plot
    report = analyzer.generate_report()
    print("Simulation Report:", report)

    analyzer.plot_disease_progression()
