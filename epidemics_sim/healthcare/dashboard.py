import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import folium
import pandas as pd
from fpdf import FPDF
from epidemics_sim.agents.base_agent import State

class CovidDashboard:
    def __init__(self):
        self.daily_stats = []
        self.total_deceased = 0
        self.daily_interactions = []
        self.hospitalized_counts = []
        self.isolated_counts = []
        self.policy_timeline = []
        self.municipal_data = {}  # Datos para mapas

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

    def plot_stacked_bar_cases(self, save_path="stacked_cases.html"):
        if not self.daily_stats:
            print("No data available for plotting.")
            return
        df = pd.DataFrame(self.daily_stats)
        df["Day"] = range(1, len(df) + 1)
        fig = px.bar(df, x="Day", y=["infected", "recovered", "deceased"],
                     labels={"value": "Number of Cases", "variable": "Case Type"},
                     title="Daily Cases Breakdown", barmode="stack")
        fig.write_html(save_path)
        print(f"Stacked bar chart saved as {save_path}")
        fig.show()

    def generate_interactive_map(self, save_path="covid_map.html"):
        if not self.municipal_data:
            print("No municipal data available for mapping.")
            return
        
        cuba_map = folium.Map(location=[23.1136, -82.3666], zoom_start=7)
        for municipio, data in self.municipal_data.items():
            folium.CircleMarker(
                location=data["coordinates"],
                radius=data["cases"] / 100,  # Ajustar el tamaño en base a casos
                color='red',
                fill=True,
                fill_color='red',
                fill_opacity=0.6,
                popup=f"{municipio}: {data['cases']} cases"
            ).add_to(cuba_map)
        
        cuba_map.save(save_path)
        print(f"COVID-19 map saved as {save_path}")

    def generate_all_visualizations(self):
        self.plot_interactive_disease_progression()
        self.plot_stacked_bar_cases()
        self.generate_interactive_map()
        print("All visualizations generated and saved.")
