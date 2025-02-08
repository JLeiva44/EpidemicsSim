import matplotlib.pyplot as plt
from fpdf import FPDF
import pandas as pd
from epidemics_sim.agents.base_agent import State

class SimulationAnalyzer:
    def __init__(self):
        self.daily_stats = []
        self.total_deceased = 0
        self.total_diagnosed = 0
        self.total_active_cases = 0
        self.total_recovered = 0
        self.hospitalized_counts = []
        self.isolated_counts = []
        self.daily_interactions = []
        self.policy_timeline = []

    def record_daily_stats(self, agents, daily_interactions, hospitalized, isolated):
        daily_deceased = sum(1 for agent in agents if agent.infection_status["state"] == State.DECEASED)
        self.total_deceased += daily_deceased
        daily_recovered = sum(1 for agent in agents if agent.infection_status["state"] == State.RECOVERED)
        self.total_recovered += daily_recovered
        daily_diagnosed = sum(1 for agent in agents if agent.infection_status["state"] == State.INFECTED)
        self.total_diagnosed += daily_diagnosed
        self.total_active_cases = daily_diagnosed

        stats = {
            "susceptible": sum(1 for agent in agents if agent.infection_status["state"] == State.SUSCEPTIBLE),
            "infected": daily_diagnosed,  # 🔹 Este es el número de casos nuevos del día
            "cumulative_cases": self.total_diagnosed,  # 🔹 Acumulado hasta ahora
            "recovered": self.total_recovered,
            "active_cases": self.total_active_cases,
            "deceased": self.total_deceased,
            "hospitalized": hospitalized,
            "isolated": isolated,
        }
        self.daily_stats.append(stats)
        self.daily_stats.append(stats)
        self.daily_interactions.append(daily_interactions)
        self.hospitalized_counts.append(hospitalized)
        self.isolated_counts.append(isolated)

    def plot_pie_chart_cases(self):
        labels = ["Active Cases", "Recovered", "Hospitalized", "Isolated", "Deceased"]
        sizes = [self.total_active_cases, self.total_recovered, sum(self.hospitalized_counts), sum(self.isolated_counts), self.total_deceased]
        plt.figure(figsize=(7, 7))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=["red", "green", "blue", "purple", "black"])
        plt.title("Distribution of Cases")
        plt.show()

    def plot_pie_chart_symptoms(self, symptomatic, asymptomatic):
        labels = ["Symptomatic", "Asymptomatic"]
        sizes = [symptomatic, asymptomatic]
        plt.figure(figsize=(7, 7))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=["orange", "cyan"])
        plt.title("Symptomatic vs Asymptomatic Cases")
        plt.show()

    def plot_daily_cases(self):
        days = range(1, len(self.daily_stats) + 1)
        daily_cases = [day["infected"] for day in self.daily_stats]
        cumulative_cases = [sum(daily_cases[:i+1]) for i in range(len(daily_cases))]
        active_cases = [self.daily_stats[i]["active_cases"] for i in range(len(daily_cases))]

        plt.figure(figsize=(10, 5))
        plt.scatter(days, daily_cases, label="Daily Cases", color="red")
        plt.plot(days, cumulative_cases, label="Cumulative Cases", color="blue", linestyle="dashed")
        plt.plot(days, active_cases, label="Active Cases", color="purple", linestyle="dotted")

        plt.title("Daily, Cumulative, and Active Cases")
        plt.xlabel("Day")
        plt.ylabel("Number of Cases")
        plt.legend()
        plt.grid()
        plt.show()


    def plot_recovery_trend(self):
        days = range(1, len(self.daily_stats) + 1)
        daily_recoveries = [day["recovered"] for day in self.daily_stats]
        cumulative_recoveries = [sum(daily_recoveries[:i+1]) for i in range(len(daily_recoveries))]
        plt.figure(figsize=(10, 5))
        plt.scatter(days, daily_recoveries, label="Daily Recoveries", color="green")
        plt.scatter(days, cumulative_recoveries, label="Cumulative Recoveries", color="blue")
        plt.title("Recovery Trends")
        plt.xlabel("Day")
        plt.ylabel("Number of Recoveries")
        plt.legend()
        plt.grid()
        plt.show()

    def plot_death_trend(self):
        days = range(1, len(self.daily_stats) + 1)
        daily_deaths = [day["deceased"] for day in self.daily_stats]
        cumulative_deaths = [sum(daily_deaths[:i+1]) for i in range(len(daily_deaths))]
        plt.figure(figsize=(10, 5))
        plt.scatter(days, daily_deaths, label="Daily Deaths", color="black")
        plt.scatter(days, cumulative_deaths, label="Cumulative Deaths", color="gray")
        plt.title("Death Trends")
        plt.xlabel("Day")
        plt.ylabel("Number of Deaths")
        plt.legend()
        plt.grid()
        plt.show()


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
