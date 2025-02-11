# import json
# import random


# demographics = {}
# covid = {}
# # Abre el archivo JSON
# with open('epidemics_sim/data/reducido.json', 'r') as archivo:
#     # Cargar los datos del archivo en un diccionario
#     demographics = json.load(archivo)

# with open('epidemics_sim/data/covid.json', 'r') as archivo:
#     # Cargar los datos del archivo en un diccionario
#     covid = json.load(archivo)


# # Controller
# from epidemics_sim.simulation.sim_controller import SimulationController

# # Disease Model
# from epidemics_sim.diseases.covid_model import CovidModel

# # Policies
# from epidemics_sim.policies.lockdown_policy import LockdownPolicy
# from epidemics_sim.policies.mask_policy import MaskUsagePolicy
# from epidemics_sim.policies.social_distancing_policy import SocialDistancingPolicy
# from epidemics_sim.policies.vaccination_policy import VaccinationPolicy
# from epidemics_sim.policies.social_distancing_policy import SocialDistancingPolicy
# from epidemics_sim.policies.vaccination_policy import VaccinationPolicy


# params = {
#     "demographics": demographics,
#     "disease" : CovidModel(
#         covid["transmission_rate"],
#         covid["incubation_period"],
#         covid["asymptomatic_probability"],
#         covid["base_mortality_rate"],
#         covid["immunity_duration"],
#         covid["recovery_rates"],
#         covid["severity_durations"],
#         covid["progression_rates"]
#         ),
#     "policies_config": {
#     "lockdown": {
#         "restricted_clusters": ["work", "school"]
#     },
#     "mask": {
#         "transmission_reduction_factor": 0.5
#     },
#     "social_distancing": {
#         "reduction_factor": 0.5
#     },
#     "vaccination": {
#         "vaccination_rate": 0.5,
#         "vaccine_efficacy": 0.8
#     }
#     },
#     "days" : 100,
#     "initial_infected": 10
# }
# CONTROLLER = SimulationController(params["demographics"],params["disease"],params["policies_config"],params["days"],params["initial_infected"])

# report = CONTROLLER.run()
# print(report)


a = [1,2,3]
a[-1] = 6
print(a)