import matplotlib.pyplot as plt
from epidemics_sim.agents.base_agent import State

class SimulationAnalyzer:
    def __init__(self):
        """
        Initialize the simulation analyzer.
        """
        self.daily_stats = []

    def record_daily_stats(self, agents):
        """
        Record statistics for the current day, focusing on disease progression.

        :param agents: List of agents in the simulation.
        """
        stats = {
            "susceptible": sum(1 for agent in agents if agent.infection_status["state"] == State.SUSCEPTIBLE),
            "infected": sum(1 for agent in agents if agent.infection_status["state"] == State.INFECTED),
            "recovered": sum(1 for agent in agents if agent.infection_status["state"] == State.RECOVERED),
            "immune": sum(1 for agent in agents if agent.immune),  # Se mantiene como atributo separado
            "deceased": sum(1 for agent in agents if agent.infection_status["state"] == State.DECEASED),
        }
        self.daily_stats.append(stats)

        # ✅ Imprimir correctamente las estadísticas
        print(f"Susceptibles: {stats['susceptible']}")
        print(f"Infectados: {stats['infected']}")
        print(f"Recuperados: {stats['recovered']}")
        print(f"Fallecidos: {stats['deceased']}")
        print(f"Inmunes: {stats['immune']}")  # 🔹 Corrección en la clave del diccionario

    def generate_report(self):
        """
        Generate a summary report of the simulation.

        :return: A dictionary containing cumulative statistics.
        """
        if not self.daily_stats:
            return {"message": "No data recorded yet."}

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
        if not self.daily_stats:
            print("No data available for plotting.")
            return

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
