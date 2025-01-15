from epidemics_sim.logger import logger
from epidemics_sim.simulation.pop_with_ser import SyntheticPopulationGenerator
import json


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

print(loaded_agents)