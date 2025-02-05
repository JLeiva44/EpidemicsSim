import matplotlib.pyplot as plt
from epidemics_sim.agents.base_agent import State

class SimulationAnalyzer:
    def __init__(self):
        """
        Initialize the simulation analyzer.
        """
        self.daily_stats = []
        self.total_deceased = 0  # 📌 Mantener un acumulador de fallecidos

    def record_daily_stats(self, agents):
        """
        Record statistics for the current day, focusing on disease progression.

        :param agents: List of agents in the simulation.
        """
        daily_deceased = sum(1 for agent in agents if agent.infection_status["state"] == State.DECEASED)
        self.total_deceased += daily_deceased  # 🔹 Acumulamos los fallecidos

        stats = {
            "susceptible": sum(1 for agent in agents if agent.infection_status["state"] == State.SUSCEPTIBLE),
            "infected": sum(1 for agent in agents if agent.infection_status["state"] == State.INFECTED),
            "recovered": sum(1 for agent in agents if agent.infection_status["state"] == State.RECOVERED),
            "immune": sum(1 for agent in agents if agent.immune),  
            "deceased": self.total_deceased,  # 📌 Usamos el acumulador
        }
        self.daily_stats.append(stats)

        # ✅ Imprimir correctamente las estadísticas
        print(f"Susceptibles: {stats['susceptible']}")
        print(f"Infectados: {stats['infected']}")
        print(f"Recuperados: {stats['recovered']}")
        print(f"Fallecidos (acumulados): {stats['deceased']}")
        print(f"Inmunes: {stats['immune']}")  

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
            "total_deceased": self.total_deceased,  # 📌 Devolvemos el acumulador
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
        plt.plot(days, deceased, label="Deceased", linestyle="--", color="black", linewidth=2)  # 🔹 Hacer la línea más visible

        plt.title("Disease Progression Over Time")
        plt.xlabel("Day")
        plt.ylabel("Number of Agents")
        plt.legend()
        plt.grid()

        plt.tight_layout()
        plt.show()

    def compute_temporal_stats(self, interval="daily"):
        """
        Compute disease progression statistics based on different time intervals.

        :param interval: Time interval for aggregation ('daily', 'weekly', 'monthly').
        :return: Dictionary with aggregated statistics.
        """
        if not self.daily_stats:
            print("No data available for temporal analysis.")
            return {}

        data_length = len(self.daily_stats)

        if interval == "daily":
            return self.daily_stats

        elif interval == "weekly":
            num_weeks = data_length // 7
            weekly_stats = []
            for i in range(num_weeks):
                week_data = self.daily_stats[i * 7: (i + 1) * 7]
                weekly_aggregated = {key: sum(day[key] for day in week_data) for key in week_data[0]}
                weekly_stats.append(weekly_aggregated)
            return weekly_stats

        elif interval == "monthly":
            num_months = data_length // 30
            monthly_stats = []
            for i in range(num_months):
                month_data = self.daily_stats[i * 30: (i + 1) * 30]
                monthly_aggregated = {key: sum(day[key] for day in month_data) for key in month_data[0]}
                monthly_stats.append(monthly_aggregated)
            return monthly_stats

        else:
            print("Invalid interval! Choose from 'daily', 'weekly', or 'monthly'.")
            return {}





# class SimulationAnalyzer:
#     def __init__(self):
#         """
#         Initialize the simulation analyzer.
#         """
#         self.daily_stats = []

#     def record_daily_stats(self, agents):
#         """
#         Record statistics for the current day, focusing on disease progression.

#         :param agents: List of agents in the simulation.
#         """
#         stats = {
#             "susceptible": sum(1 for agent in agents if agent.infection_status["state"] == State.SUSCEPTIBLE),
#             "infected": sum(1 for agent in agents if agent.infection_status["state"] == State.INFECTED),
#             "recovered": sum(1 for agent in agents if agent.infection_status["state"] == State.RECOVERED),
#             "immune": sum(1 for agent in agents if agent.immune),  # Se mantiene como atributo separado
#             "deceased": sum(1 for agent in agents if agent.infection_status["state"] == State.DECEASED),
#         }
#         self.daily_stats.append(stats)

#         # ✅ Imprimir correctamente las estadísticas
#         print(f"Susceptibles: {stats['susceptible']}")
#         print(f"Infectados: {stats['infected']}")
#         print(f"Recuperados: {stats['recovered']}")
#         print(f"Fallecidos: {stats['deceased']}")
#         print(f"Inmunes: {stats['immune']}")  # 🔹 Corrección en la clave del diccionario

#     def generate_report(self):
#         """
#         Generate a summary report of the simulation.

#         :return: A dictionary containing cumulative statistics.
#         """
#         if not self.daily_stats:
#             return {"message": "No data recorded yet."}

#         report = {
#             "total_days": len(self.daily_stats),
#             "total_susceptible": sum(day["susceptible"] for day in self.daily_stats),
#             "total_infected": sum(day["infected"] for day in self.daily_stats),
#             "total_recovered": sum(day["recovered"] for day in self.daily_stats),
#             "total_immune": sum(day["immune"] for day in self.daily_stats),
#             "total_deceased": sum(day["deceased"] for day in self.daily_stats),
#         }
#         return report

#     def plot_disease_progression(self):
#         """
#         Plot the daily statistics related to disease progression using matplotlib.
#         """
#         if not self.daily_stats:
#             print("No data available for plotting.")
#             return

#         days = range(1, len(self.daily_stats) + 1)
#         susceptible = [day["susceptible"] for day in self.daily_stats]
#         infected = [day["infected"] for day in self.daily_stats]
#         recovered = [day["recovered"] for day in self.daily_stats]
#         immune = [day["immune"] for day in self.daily_stats]
#         deceased = [day["deceased"] for day in self.daily_stats]

#         plt.figure(figsize=(10, 6))

#         plt.plot(days, susceptible, label="Susceptible", color="blue")
#         plt.plot(days, infected, label="Infected", color="red")
#         plt.plot(days, recovered, label="Recovered", color="green")
#         plt.plot(days, immune, label="Immune", color="purple")
#         plt.plot(days, deceased, label="Deceased", linestyle="--", color="black")

#         plt.title("Disease Progression Over Time")
#         plt.xlabel("Day")
#         plt.ylabel("Number of Agents")
#         plt.legend()
#         plt.grid()

#         plt.tight_layout()
#         plt.show()
