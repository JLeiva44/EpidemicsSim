from epidemics_sim.logger import logger
from epidemics_sim.simulation.synthetic_population import SyntheticPopulationGenerator
import json
from epidemics_sim.simulation.city_cluster import CityClusterGenerator
from epidemics_sim.simulation.clusters_whit_subclusters import ClusterWithSubclusters


demographics = {}
# Abre el archivo JSON
with open('epidemics_sim/data/test.json', 'r') as archivo:
    # Cargar los datos del archivo en un diccionario
    demographics = json.load(archivo)

#logger.info(demographics) # Done

population_generator = SyntheticPopulationGenerator(demographics)

population = population_generator.generate_population()
 
#Guardar la población en un archivo
population_generator.save_population(population, 'population.pkl')

# Cargar la población desde el archivo
loaded_agents = population_generator.load_population('population.pkl')

print("poblacion hecha")

