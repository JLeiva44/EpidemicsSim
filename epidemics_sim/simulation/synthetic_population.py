import pickle  # Para serialización y deserialización
from epidemics_sim.agents.human_agent import HumanAgent
import random

def get_large_household_size():
    distribution = {5: 0.5, 6: 0.3, 7: 0.15, 8: 0.05}
    return random.choices(list(distribution.keys()), list(distribution.values()))[0]

size_mapping = {
    "1_persona": 1,
    "2_personas": 2,
    "3_personas": 3,
    "4_personas": 4,
    "5_personas_o_mas": get_large_household_size
}

class SyntheticPopulationGenerator:
    def __init__(self, demographics):
        """
        Clase para generar una población sintética basada en los datos demográficos.
        
        :param demographics: Diccionario con datos demográficos.
        """
        self.demographics = demographics
        self.comorbidities_rates = demographics.get("Comorbilidades", {})  # Tasa de comorbilidades por mil
        self.population = {}
        self.agent_counter = 0 # Contador de agentes
    def generate_population(self):
        """
        Genera una población de agentes con atributos demográficos.
        """
        self._generate_agents()
        return self.population

    def save_population(self, agents, filepath):
        with open(filepath, 'wb') as file:
            pickle.dump(agents, file)
        print(f"Población guardada en {filepath}.")

    def load_population(self, filepath):
        with open(filepath, 'rb') as file:
            agents = pickle.load(file)
        print(f"Población cargada desde {filepath}.")
        return agents

    def _generate_agents(self):
        #agents = {}
        for municipio, data in self.demographics["municipios"].items():
            # if "population" not in data:
            #     continue  # Ignorar claves generales como "Comorbilidades"

            num_male = int(data["population"].get("VARONES", 0))
            num_female = int(data["population"].get("HEMBRAS", 0))

            self._create_agents(num_male, "male", municipio, data)
            self._create_agents(num_female, "female", municipio, data)
        
        #return agents

    def _create_agents(self, num_agents, gender, municipio, data):
        #agents = []
        #agents = {}
        for _ in range(num_agents):
            age = self._generate_age(data["population"]["Habitantes_por_edad"])
            occupation = self._generate_occupation(age)
            comorbidities = self._generate_comorbidities()
            
            # Generar un ID único para cada agente
            agent_id = self.agent_counter
            self.agent_counter += 1
            
            agent = HumanAgent(
                agent_id, age, gender, occupation, None, municipio, None, comorbidities
            )
            self.population[agent_id] = agent
        #return agents

    def _generate_age(self, age_distribution):
        ranges = list(age_distribution.keys())
        probabilities = [float(age_distribution[r]) for r in ranges]
        chosen_range = random.choices(ranges, probabilities)[0]

        if chosen_range == "0-15":
            return random.randint(0, 15)
        elif chosen_range == "16-59":
            return random.randint(16, 59)
        elif chosen_range == "60 y +":
            return random.randint(60, 100)

    def _generate_occupation(self, age):
        if age < 18:
            return "student"
        elif 18 <= age <= 22 and random.random() < 0.5: # 50 % de probabilidad
            return "worker"
        else:
            return "retired"

    def _generate_comorbidities(self):
        comorbidities = {}
        for disease, rate_per_thousand in self.comorbidities_rates.items():
            probability = float(rate_per_thousand) / 1000  # Convertimos tasa por mil a probabilidad 0-1
            comorbidities[disease] = random.random() < probability
        return comorbidities
