import json
import random


demographics = {}
# Abre el archivo JSON
with open('epidemics_sim/data/reducido.json', 'r') as archivo:
    # Cargar los datos del archivo en un diccionario
    demographics = json.load(archivo)
0
#print(diccionario)
def inc ():
    return random.randint(4, 7)
# Other Data
example_config = {
    "home": {"duration_mean": 480, "duration_std": 120},
    "work": {"duration_mean": 480, "duration_std": 120, "min_links": 2},
    "school": {"duration_mean": 300, "duration_std": 60},
    "shopping": {"duration_mean": 37, "duration_std": 10, "max_agents": 50},
    "transport": {"interval": 5, "duration_mean": 15, "duration_std": 5},
    "disease":{
    "transmission_rate": 0.6,  # Probabilidad de transmisión por contacto
    "incubation_period": inc,   # Período de incubación en días
    "asymptomatic_probability": 0.4,  # Probabilidad de que un agente sea asintomático
    "base_mortality_rate": 0.2,  # Tasa de mortalidad base para casos críticos
}

}

# Controller
from epidemics_sim.simulation.sim_controller import SimulationController

# Disease Model
from epidemics_sim.diseases.covid_model import CovidModel

# Policies
from epidemics_sim.policies.lockdown_policy import LockdownPolicy
from epidemics_sim.policies.mask_policy import MaskUsagePolicy
from epidemics_sim.policies.social_distancing_policy import SocialDistancingPolicy
from epidemics_sim.policies.vaccination_policy import VaccinationPolicy
from epidemics_sim.policies.social_distancing_policy import SocialDistancingPolicy
from epidemics_sim.policies.vaccination_policy import VaccinationPolicy


policies = [LockdownPolicy(),MaskUsagePolicy(), SocialDistancingPolicy(), VaccinationPolicy()]
sim_days = 100
CONTROLLER = SimulationController(demographics,example_config,CovidModel,policies,sim_days)

report = CONTROLLER.run()
print(report)

