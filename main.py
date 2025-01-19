import json


demographics = {}
# Abre el archivo JSON
with open('epidemics_sim/data/habana.json', 'r') as archivo:
    # Cargar los datos del archivo en un diccionario
    demographics = json.load(archivo)

#print(diccionario)

# Other Data
example_config = {
    "home": {"duration_mean": 480, "duration_std": 120},
    "work": {"duration_mean": 480, "duration_std": 120, "min_links": 2},
    "school": {"duration_mean": 300, "duration_std": 60},
    "shopping": {"duration_mean": 37, "duration_std": 10, "max_agents": 50},
    "transport": {"interval": 5, "duration_mean": 15, "duration_std": 5},
    "household_sizes": [1, 2, 3, 4, 5, 6],
    "household_distribution": [0.1, 0.2, 0.3, 0.2, 0.15, 0.05],
    "work_sizes": [5, 10, 20, 50],
    "work_distribution": [0.4, 0.3, 0.2, 0.1],
    "school_sizes": [20, 30, 40],
    "school_distribution": [0.5, 0.3, 0.2],
    "shopping_centers": 5,
    "disease": {"transmission_rate": 0.03, "recovery_rate": 0.85, "mortality_rate": 0.01}
}

# Controller
from epidemics_sim.simulation.sim_controller import SimulationController

# Disease Model
from epidemics_sim.diseases.covid_model import CovidModel

# Policies
from epidemics_sim.policies.lockdown_policy import LockdownPolicy
from epidemics_sim.policies.social_distancing_policy import SocialDistancingPolicy
from epidemics_sim.policies.vaccination_policy import VaccinationPolicy



CONTROLLER = SimulationController(demographics,example_config,CovidModel,[LockdownPolicy, SocialDistancingPolicy, VaccinationPolicy],10)

report = CONTROLLER.run()

