import matplotlib.pyplot as plt
from fpdf import FPDF
import pandas as pd
from epidemics_sim.agents.base_agent import State

class SimulationAnalyzer:
    def __init__(self):
        """
        Initialize the simulation analyzer.
        """
        self.daily_stats = []
        self.total_deceased = 0  # 📌 Mantener un acumulador de fallecidos
        self.daily_interactions = []
        self.hospitalized_counts = []
        self.isolated_counts = []
        self.policy_timeline = []  # Lista para rastrear cuándo se aplican políticas


    def record_daily_stats(self, agents, daily_interactions, hospitalized, isolated):
        """
        Record statistics for the current day, focusing on disease progression.

        :param agents: List of agents in the simulation.
        :param daily_interactions: Number of interactions for the day.
        :param hospitalized: Number of hospitalized agents.
        :param isolated: Number of isolated agents.
        :param applied_policies: List of policies applied on this day (optional).
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
        # if applied_policies:
        #     self.policy_timeline.append((day, applied_policies))

        self.daily_interactions.append(daily_interactions)
        self.hospitalized_counts.append(hospitalized)
        self.isolated_counts.append(isolated)

    def record_policy(self, day, applied_policies):
        self.policy_timeline.append((day, applied_policies))

    def plot_interactions(self):
        """
        Plot the daily number of interactions over time.
        """
        if not self.daily_interactions:
            print("No interaction data available for plotting.")
            return

        days = range(1, len(self.daily_interactions) + 1)
        plt.figure(figsize=(10, 5))
        plt.plot(days, self.daily_interactions, label="Daily Interactions", color="orange")
        plt.title("Number of Interactions Over Time")
        plt.xlabel("Day")
        plt.ylabel("Interactions")
        plt.legend()
        plt.grid()
        plt.show()

    def plot_hospitalization_and_isolation(self):
        """
        Plot the daily number of hospitalized and isolated agents over time.
        """
        if not self.hospitalized_counts or not self.isolated_counts:
            print("No hospitalization or isolation data available for plotting.")
            return

        days = range(1, len(self.hospitalized_counts) + 1)
        plt.figure(figsize=(10, 5))
        plt.plot(days, self.hospitalized_counts, label="Hospitalized", color="red")
        plt.plot(days, self.isolated_counts, label="Isolated", color="blue")
        plt.title("Hospitalization and Isolation Over Time")
        plt.xlabel("Day")
        plt.ylabel("Number of Agents")
        plt.legend()
        plt.grid()
        plt.show()

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

        # Añadir marcadores de políticas
        for day, policies in self.policy_timeline:
            plt.axvline(x=day, color='gray', linestyle='--', alpha=0.5)
            plt.text(day, max(infected) * 0.9, ', '.join(policies), rotation=90, verticalalignment='top', fontsize=8)

        plt.title("Disease Progression Over Time")
        plt.xlabel("Day")
        plt.ylabel("Number of Agents")
        plt.legend()
        plt.grid()

        plt.tight_layout()
        plt.show()

    def plot_policy_timeline(self):
        """
        Plot a timeline of when policies were applied.
        """
        if not self.policy_timeline:
            print("No policy data available.")
            return

        days, policies = zip(*self.policy_timeline)
        plt.figure(figsize=(10, 4))
        plt.scatter(days, [1] * len(days), marker='o', color='black')
        for day, policy in zip(days, policies):
            plt.text(day, 1.05, ', '.join(policy), rotation=45, ha='right', fontsize=9)

        plt.title("Policy Application Timeline")
        plt.xlabel("Day")
        plt.yticks([])
        plt.grid(axis='x', linestyle='--', alpha=0.7)
        plt.show()

    def export_to_csv(self, filename="simulation_results.csv"):
        """
        Export daily statistics to a CSV file.
        """
        df = pd.DataFrame(self.daily_stats)
        df.to_csv(filename, index=False)
        print(f"Simulation data exported to {filename}")

    def generate_pdf_report(self, filename="simulation_report.pdf"):
        """
        Generate a PDF report with summary statistics and plots.
        """
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", style="B", size=16)
        pdf.cell(200, 10, "Simulation Report", ln=True, align="C")
        pdf.ln(10)
        
        pdf.set_font("Arial", size=12)
        summary = self.generate_report()
        for key, value in summary.items():
            pdf.cell(0, 10, f"{key}: {value}", ln=True)
        
        pdf.output(filename)
        print(f"Simulation report saved as {filename}")

    def generate_report(self):
        """
        Generate a summary report of the simulation.
        """
        if not self.daily_stats:
            return {"message": "No data recorded yet."}

        report = {
            "total_days": len(self.daily_stats),
            "total_susceptible": sum(day["susceptible"] for day in self.daily_stats),
            "total_infected": sum(day["infected"] for day in self.daily_stats),
            "total_recovered": sum(day["recovered"] for day in self.daily_stats),
            "total_immune": sum(day["immune"] for day in self.daily_stats),
            "total_deceased": self.total_deceased,
        }
        return report