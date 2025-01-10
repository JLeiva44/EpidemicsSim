from epidemics_sim.agents.human_agent import HumanAgent
import random

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
        self._assign_households(agents)
        return agents

    def _generate_agents(self):
        """
        Generate agents with attributes based on demographics.

        :return: A list of agents.
        """
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
        """
        Assign agents to households based on municipal data, ensuring each household has at least one adult.

        :param agents: List of agents.
        """
        for municipio, data in self.demographics["municipios"].items():
            municipio_agents = [agent for agent in agents if agent.municipio == municipio]
            households = []
            unassigned_agents = municipio_agents.copy()

            household_sizes = list(data["hogares_por_tamano"].keys())
            size_probabilities = list(data["hogares_por_tamano"].values())

            while unassigned_agents:
                size = random.choices(household_sizes, size_probabilities)[0]
                size = min(size, len(unassigned_agents))

                household = unassigned_agents[:size]
                unassigned_agents = unassigned_agents[size:]

                if not any(agent.age >= 18 for agent in household):
                    adults = [agent for agent in municipio_agents if agent.age >= 18 and agent not in household]
                    if adults:
                        household[-1] = adults[0]
                        unassigned_agents.append(adults[0])

                household_id = household[0].agent_id
                for agent in household:
                    agent.household_id = household_id

                households.append(household)

    def _generate_comorbidities(self, age, gender, municipio):
        """
        Generate comorbidities based on the demographics distribution for the agent's municipio.

        :param age: Age of the agent.
        :param gender: Gender of the agent.
        :param municipio: Municipality of the agent.
        :return: A dictionary of comorbidities for an agent.
        """
        municipio_data = self.demographics["municipios"][municipio]
        comorbidities = {}

        for comorbidity, rate in municipio_data["comorbilidades"].items():
            comorbidities[comorbidity] = random.random() < (rate / 100)

        return comorbidities

    def _generate_occupation(self, age):
        """
        Generate an occupation based on the agent's age.

        :param age: Age of the agent.
        :return: The occupation of the agent.
        """
        if age < 18:
            return "student"
        elif age < 65:
            return "worker"
        else:
            return "retired"

    def _generate_age(self, age_distribution):
        """
        Generate an age based on the age distribution for a municipio.

        :param age_distribution: Dictionary of age ranges and their probabilities.
        :return: An integer representing the age of an agent.
        """
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
        """
        Generate a gender based on a 50/50 distribution.

        :return: A string representing the gender of an agent.
        """
        return random.choice(["male", "female"])

# Example usage
if __name__ == "__main__":
    # Replace this with actual demographic data loaded from JSON
    demographics_data = {
        "municipios": {
            "Municipio1": {
                "poblacion_total": 100,
                "hogares_por_tamano": {
                    "1_persona": 14.8,
                    "2_personas": 24.7,
                    "3_personas": 22.9,
                    "4_personas": 21.1,
                    "5_personas_o_mas": 16.5
                },
                "comorbilidades": {
                    "diabetes": 10.1,
                    "hipertension": 30.9,
                    "obesidad": 18.0,
                    "tabaquismo": 19.0,
                    "asma": 8.2
                },
                "distribucion_edad": {
                    "0-17": 26.5,
                    "18-64": 60.5,
                    "65+": 13.0
                }
            }
        }
    }

    generator = SyntheticPopulationGenerator(demographics=demographics_data)
    population = generator.generate_population()
    print(f"Generated {len(population)} agents.")
