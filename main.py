import json


demographics = {}
# Abre el archivo JSON
with open('epidemics_sim/data/test.json', 'r') as archivo:
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
    "disease":{
    "transmission_rate": 0.9,  # Probabilidad de transmisión por contacto
    "incubation_period": 5,   # Período de incubación en días
    "asymptomatic_probability": 0.4,  # Probabilidad de que un agente sea asintomático
    "base_mortality_rate": 0.02,  # Tasa de mortalidad base para casos críticos
}

}

# Controller
from epidemics_sim.simulation.sim_controller import SimulationController

# Disease Model
from epidemics_sim.diseases.covid_model import CovidModel

# Policies
from epidemics_sim.policies.lockdown_policy import LockdownPolicy
from epidemics_sim.policies.social_distancing_policy import SocialDistancingPolicy
from epidemics_sim.policies.vaccination_policy import VaccinationPolicy



CONTROLLER = SimulationController(demographics,example_config,CovidModel,[LockdownPolicy, SocialDistancingPolicy, VaccinationPolicy],100)

report = CONTROLLER.run()
print(report)

