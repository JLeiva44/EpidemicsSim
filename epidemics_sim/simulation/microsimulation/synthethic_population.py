from epidemics_sim.agents.human_agent import HumanAgent
import random

class SyntheticPopulationGenerator:
    def __init__(self, demographics):
        """
        Class to generate a synthetic population.

        :param demographics: Dictionary with demographic data (e.g., age distribution, gender ratio).
        """
        self.demographics = demographics
        self.num_agents = demographics.get("num_agents", 100)

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
        for agent_id in range(self.num_agents):
            age = self._generate_age()
            gender = self._generate_gender()
            occupation = self._generate_occupation(age)
            municipio = self._generate_municipio()
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
        household_sizes_by_municipio = self.demographics.get("household_size_distribution_by_municipio", {})
        household_probabilities_by_municipio = self.demographics.get("household_size_probabilities_by_municipio", {})
        num_households_by_municipio = self.demographics.get("households_by_municipio", {})

        for municipio, num_households in num_households_by_municipio.items():
            municipio_agents = [agent for agent in agents if agent.municipio == municipio]
            households = []
            unassigned_agents = municipio_agents.copy()

            household_sizes = household_sizes_by_municipio.get(municipio, [1, 2, 3, 4, 5, 6, 7])
            size_probabilities = household_probabilities_by_municipio.get(municipio, [0.3, 0.25, 0.2, 0.15, 0.05, 0.03, 0.02])

            while len(households) < num_households and unassigned_agents:
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
        municipio_comorbidities = self.demographics.get("comorbidity_distribution_by_municipio", {}).get(municipio, {})
        comorbidities = {}

        for comorbidity, rules in municipio_comorbidities.items():
            probability = rules.get("base", 0)

            if "age" in rules:
                for age_range, adjusted_prob in rules["age"].items():
                    min_age = int(age_range.split("+")[0]) if "+" in age_range else None
                    if min_age and age >= min_age:
                        probability = adjusted_prob

            if "gender" in rules:
                probability = rules["gender"].get(gender, probability)

            comorbidities[comorbidity] = random.random() < probability

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

    def _generate_age(self):
        """
        Generate an age based on the demographics distribution.

        :return: An integer representing the age of an agent.
        """
        age_distribution = self.demographics.get("age_distribution", {
            "0-17": 0.25,
            "18-64": 0.6,
            "65+": 0.15
        })

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
        Generate a gender based on the demographics distribution.

        :return: A string representing the gender of an agent.
        """
        gender_distribution = self.demographics.get("gender_distribution", {
            "male": 0.5,
            "female": 0.5
        })

        genders = list(gender_distribution.keys())
        probabilities = list(gender_distribution.values())
        return random.choices(genders, probabilities)[0]

    def _generate_municipio(self):
        """
        Assign a municipio to the agent based on demographics.

        :return: The name or ID of the municipio.
        """
        municipio_distribution = self.demographics.get("municipio_distribution", {
            "Municipio_1": 0.4,
            "Municipio_2": 0.35,
            "Municipio_3": 0.25
        })

        municipios = list(municipio_distribution.keys())
        probabilities = list(municipio_distribution.values())
        return random.choices(municipios, probabilities)[0]

# Example usage
if __name__ == "__main__":
    demographics_data = {
        "num_agents": 100,
        "age_distribution": {
            "0-17": 0.25,
            "18-64": 0.6,
            "65+": 0.15
        },
        "gender_distribution": {
            "male": 0.5,
            "female": 0.5
        },
        "household_size_distribution_by_municipio": {
            "Municipio_1": [1, 2, 3, 4, 5],
            "Municipio_2": [2, 3, 4, 5, 6],
            "Municipio_3": [1, 3, 4, 5]
        },
        "household_size_probabilities_by_municipio": {
            "Municipio_1": [0.2, 0.3, 0.25, 0.15, 0.1],
            "Municipio_2": [0.1, 0.25, 0.3, 0.2, 0.15],
            "Municipio_3": [0.3, 0.2, 0.25, 0.15]
        },
        "households_by_municipio": {
            "Municipio_1": 30,
            "Municipio_2": 15,
            "Municipio_3": 5
        },
        "municipio_distribution": {
            "Municipio_1": 0.4,
            "Municipio_2": 0.35,
            "Municipio_3": 0.25
        },
        "comorbidity_distribution_by_municipio": {
            "Municipio_1": {
                "diabetes": {"base": 0.1, "age": {"40+": 0.2}},
                "hypertension": {"base": 0.15, "age": {"40+": 0.3}},
                "obesity": {"base": 0.2}
            },
            "Municipio_2": {
                "diabetes": {"base": 0.12, "age": {"40+": 0.25}},
                "hypertension": {"base": 0.18, "age": {"40+": 0.35}},
                "obesity": {"base": 0.22}
            },
            "Municipio_3": {
                "diabetes": {"base": 0.08, "age": {"40+": 0.15}},
                "hypertension": {"base": 0.1, "age": {"40+": 0.2}},
                "obesity": {"base": 0.18}
            }
        }
    }

    generator = SyntheticPopulationGenerator(demographics=demographics_data)
    population = generator.generate_population()
    print(f"Generated {len(population)} agents.")
