import matplotlib.pyplot as plt

class SimulationAnalyzer:
    def __init__(self):
        """
        Initialize the simulation analyzer.
        """
        self.daily_stats = []

    def record_daily_stats(self, agents, healthcare_system):
        """
        Record statistics for the current day, including healthcare system metrics.

        :param agents: List of agents in the simulation.
        :param healthcare_system: Instance of HealthcareSystem to track healthcare-related stats.
        """
        stats = {
            "susceptible": sum(1 for agent in agents if agent.infection_status["state"] == "susceptible"),
            "infected": sum(1 for agent in agents if agent.infection_status["state"] == "infected"),
            "recovered": sum(1 for agent in agents if agent.infection_status["state"] == "recovered"),
            "immune": sum(1 for agent in agents if agent.immune),
            "deceased": sum(1 for agent in agents if agent.infection_status["state"] == "deceased"),
            "consultorio_occupancy": healthcare_system.get_level_occupancy("consultorio"),
            "policlinico_occupancy": healthcare_system.get_level_occupancy("policlinico"),
            "hospital_occupancy": healthcare_system.get_level_occupancy("hospital"),
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
            "average_consultorio_occupancy": sum(day["consultorio_occupancy"] for day in self.daily_stats) / len(self.daily_stats),
            "average_policlinico_occupancy": sum(day["policlinico_occupancy"] for day in self.daily_stats) / len(self.daily_stats),
            "average_hospital_occupancy": sum(day["hospital_occupancy"] for day in self.daily_stats) / len(self.daily_stats),
        }
        return report

    def plot_statistics(self):
        """
        Plot the daily statistics using matplotlib.
        """
        days = range(1, len(self.daily_stats) + 1)
        susceptible = [day["susceptible"] for day in self.daily_stats]
        infected = [day["infected"] for day in self.daily_stats]
        recovered = [day["recovered"] for day in self.daily_stats]
        immune = [day["immune"] for day in self.daily_stats]
        deceased = [day["deceased"] for day in self.daily_stats]
        consultorio = [day["consultorio_occupancy"] for day in self.daily_stats]
        policlinico = [day["policlinico_occupancy"] for day in self.daily_stats]
        hospital = [day["hospital_occupancy"] for day in self.daily_stats]

        plt.figure(figsize=(12, 8))

        # Disease progression
        plt.subplot(2, 1, 1)
        plt.plot(days, susceptible, label="Susceptible")
        plt.plot(days, infected, label="Infected")
        plt.plot(days, recovered, label="Recovered")
        plt.plot(days, immune, label="Immune")
        plt.plot(days, deceased, label="Deceased", linestyle="--", color="black")
        plt.title("Disease Progression Over Time")
        plt.xlabel("Day")
        plt.ylabel("Number of Agents")
        plt.legend()
        plt.grid()

        # Healthcare system metrics
        plt.subplot(2, 1, 2)
        plt.plot(days, consultorio, label="Consultorio Occupancy", linestyle="--")
        plt.plot(days, policlinico, label="Policlinico Occupancy", linestyle="-.")
        plt.plot(days, hospital, label="Hospital Occupancy", linestyle=":")
        plt.title("Healthcare System Utilization")
        plt.xlabel("Day")
        plt.ylabel("Number of Patients")
        plt.legend()
        plt.grid()

        plt.tight_layout()
        plt.show()
