import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
from fpdf import FPDF
from epidemics_sim.agents.base_agent import State

class SimulationAnalyzer:
    def __init__(self):
        self.daily_stats = []
        self.total_deceased = 0
        self.daily_interactions = []
        self.hospitalized_counts = []
        self.isolated_counts = []
        self.policy_timeline = []

    def record_daily_stats(self, agents, daily_interactions, hospitalized, isolated):
        daily_deceased = sum(1 for agent in agents if agent.infection_status["state"] == State.DECEASED)
        self.total_deceased += daily_deceased
        stats = {
            "susceptible": sum(1 for agent in agents if agent.infection_status["state"] == State.SUSCEPTIBLE),
            "infected": sum(1 for agent in agents if agent.infection_status["state"] == State.INFECTED),
            "recovered": sum(1 for agent in agents if agent.infection_status["state"] == State.RECOVERED),
            "immune": sum(1 for agent in agents if agent.immune),
            "deceased": self.total_deceased,
        }
        self.daily_stats.append(stats)
        self.daily_interactions.append(daily_interactions)
        self.hospitalized_counts.append(hospitalized)
        self.isolated_counts.append(isolated)

    def save_matplotlib_plot(self, fig, filename):
        fig.savefig(filename)
        print(f"Graph saved as {filename}")

    def plot_interactions(self, save_path="interactions.png"):
        if not self.daily_interactions:
            print("No interaction data available for plotting.")
            return
        days = range(1, len(self.daily_interactions) + 1)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(days, self.daily_interactions, label="Daily Interactions", color="orange")
        ax.set_title("Number of Interactions Over Time")
        ax.set_xlabel("Day")
        ax.set_ylabel("Interactions")
        ax.legend()
        ax.grid()
        self.save_matplotlib_plot(fig, save_path)
        plt.show()

    def plot_interactive_disease_progression(self, save_path="disease_progression.html"):
        if not self.daily_stats:
            print("No data available for plotting.")
            return
        df = pd.DataFrame(self.daily_stats)
        df["Day"] = range(1, len(df) + 1)
        fig = px.line(df, x="Day", y=["susceptible", "infected", "recovered", "immune", "deceased"],
                      labels={"value": "Number of Agents", "variable": "Category"},
                      title="Disease Progression Over Time", markers=True)
        fig.write_html(save_path)
        print(f"Interactive graph saved as {save_path}")
        fig.show()

    def generate_all_plots(self):
        self.plot_interactions()
        self.plot_interactive_disease_progression()
        print("All plots generated and saved.")
