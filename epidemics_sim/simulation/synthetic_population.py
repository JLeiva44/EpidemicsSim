import pickle  # Para serialización y deserialización
from epidemics_sim.agents.human_agent import HumanAgent
import random

# Para "5_personas_o_mas", distribuir entre 5 y un máximo configurable
def get_large_household_size():
    distribution = {5: 0.5, 6: 0.3, 7: 0.15, 8: 0.05}  # Probabilidades para tamaños mayores
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
        Class to generate a synthetic population.

        :param demographics: Dictionary with demographic data (e.g., age distribution, gender ratio).
        """
        self.demographics = demographics

    def generate_population(self):
        """
        Generate a population of agents with demographic attributes.

        :return: A list of agents.
        """
        agents = self._generate_agents()
        #self._assign_households(agents)
        return agents

    def save_population(self, agents, filepath):
        """
        Serialize and save the population to a file.

        :param agents: List of agents to save.
        :param filepath: Path to the file where the population will be saved.
        """
        with open(filepath, 'wb') as file:
            pickle.dump(agents, file)
        print(f"Population saved to {filepath}.")

    def load_population(self, filepath):
        """
        Load a population from a serialized file.

        :param filepath: Path to the file where the population is saved.
        :return: A list of agents.
        """
        with open(filepath, 'rb') as file:
            agents = pickle.load(file)
        print(f"Population loaded from {filepath}.")
        return agents

    def _generate_agents(self):
        agents = []
        for municipio, data in self.demographics["municipios"].items():
            num_agents = data["poblacion_total"]
            for agent_id in range(num_agents):
                age = self._generate_age(data["distribucion_edad"])
                gender = self._generate_gender()
                occupation = self._generate_occupation(age)
                comorbidities = self._generate_comorbidities(age, gender, municipio)

                agent = HumanAgent(
                    agent_id, age, gender, occupation, None, municipio, None, comorbidities
                )
                agents.append(agent)
        return agents

    def _assign_households(self, agents):
        for municipio, data in self.demographics["municipios"].items():
            municipio_agents = [agent for agent in agents if agent.municipio == municipio]
            adult = [agent for agent in municipio_agents if agent.age >= 18]
            households = []
            unassigned_agents = municipio_agents.copy()

            household_sizes = list(data["hogares_por_tamano"].keys())
            size_probabilities = list(data["hogares_por_tamano"].values())

            previous_length = len(unassigned_agents)
            while unassigned_agents:
                size_key = random.choices(household_sizes, size_probabilities)[0]
                size = size_mapping[size_key] if isinstance(size_mapping[size_key], int) else size_mapping[size_key]()
                size = min(size, len(unassigned_agents))

                household = unassigned_agents[:size]
                unassigned_agents = unassigned_agents[size:]

                if not any(agent.age >= 18 for agent in household):
                    adults = [agent for agent in unassigned_agents if agent.age >= 18]
                    if adults:
                        adult = adults.pop(0)
                        household[-1] = adult
                        unassigned_agents.remove(adult)

                household_id = household[0].agent_id
                for agent in household:
                    agent.household_id = household_id

                households.append(household)

                if len(unassigned_agents) == previous_length:
                    break
                previous_length = len(unassigned_agents)

    def _generate_comorbidities(self, age, gender, municipio):
        municipio_data = self.demographics["municipios"][municipio]
        comorbidities = {}

        for comorbidity, rate in municipio_data["comorbilidades"].items():
            comorbidities[comorbidity] = random.random() < (rate / 100)

        return comorbidities

    def _generate_occupation(self, age): # TODO Arreglar esto
        if age < 18:
            return "student"
        elif age < 65:
            return "worker"
        else:
            return "retired"

    def _generate_age(self, age_distribution):
        ranges = list(age_distribution.keys())
        probabilities = list(age_distribution.values())

        chosen_range = random.choices(ranges, probabilities)[0]
        if chosen_range == "0-17":
            return random.randint(0, 17)
        elif chosen_range == "18-64":
            return random.randint(18, 64)
        elif chosen_range == "65+":
            return random.randint(65, 100)

    def _generate_gender(self):
        return random.choice(["male", "female"])
