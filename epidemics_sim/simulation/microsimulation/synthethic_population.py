from epidemics_sim.agents.human_agent import HumanAgent
import random

#TODO: Se esta asignando como estudiantes a los ninos de 2 y 3 anos ARREGLAR
class SyntheticPopulationGenerator:
    def __init__(self,demographics):
        """
        Class to generate a synthetic population.

        :param num_agents: Total number of agents to generate.
        :param demographics: Dictionary with demographic data (e.g., age distribution, gender ratio).
        """
        self.demographics = demographics
        self.num_agents = demographics.get("num_agents", 100)

    def generate_population(self):
        """
        Generate a population of agents with demographic attributes.

        :return: A tuple containing households and agents.
        """
        agents = self._generate_agents()
        #households = self._generate_households(agents)
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
            comorbidities = self._generate_comorbidities(age, gender)

            agent = HumanAgent( # id, age, gender, occupation, household_id, infection_status, comorbidities=[], attributes={},initial_state=State.SUSCEPTIBLE
                agent_id, age,gender, occupation, None,None, comorbidities
            )

            agents.append(agent)
        return agents

    def _generate_households(self, agents):
        """
        Generate households ensuring each has at least one member aged 18 or older.

        :param agents: List of agents.
        :return: A list of households with agents.
        """
        household_sizes = self.demographics.get("household_size_distribution", [1, 2, 3, 4, 5, 6, 7])
        size_probabilities = self.demographics.get("household_size_probabilities", [0.3, 0.25, 0.2, 0.15, 0.05, 0.03, 0.02])
        num_households = self.demographics.get("num_households", len(agents) // 3)

        households = []
        unassigned_agents = agents.copy()

        while len(households) < num_households and unassigned_agents:
            size = random.choices(household_sizes, size_probabilities)[0]

            # Ensure there are enough agents left to form a household
            if len(unassigned_agents) < size:
                size = len(unassigned_agents)

            # Select agents for the household
            household = unassigned_agents[:size]

            # Check if there's at least one adult (age >= 18)
            if not any(agent.age >= 18 for agent in household):
                # Add one adult if available
                adults = [agent for agent in unassigned_agents if agent.age >= 18]
                if adults:
                    household[-1] = adults[0]
                    unassigned_agents.remove(adults[0])

            # Assign household ID and remove agents from the unassigned list
            household_id = household[0].agent_id
            for agent in household:
                agent.household_id = household_id
            households.append(household)
            unassigned_agents = [agent for agent in unassigned_agents if agent not in household]

        return households

    def _generate_comorbidities(self, age, gender):
        """
        Generate comorbidities based on the demographics distribution.

        :param age: Age of the agent.
        :param gender: Gender of the agent.
        :return: A dictionary of comorbidities for an agent.
        """
        comorbidity_distribution = self.demographics.get("comorbidity_distribution", {
            "diabetes": {"base": 0.1, "age": {"40+": 0.2}},
            "hypertension": {"base": 0.15, "age": {"40+": 0.3}},
            "obesity": {"base": 0.2},
            "smoking": {"base": 0.25, "gender": {"male": 0.3, "female": 0.2}},
            "copd": {"base": 0.05, "age": {"50+": 0.1}},
            "chronic_heart_disease": {"base": 0.07, "age": {"50+": 0.15}},
            "chronic_kidney_disease": {"base": 0.03}
        })

        comorbidities = {}
        for comorbidity, rules in comorbidity_distribution.items():
            probability = rules.get("base", 0)

            # Adjust probability based on age
            if "age" in rules:
                for age_range, adjusted_prob in rules["age"].items():
                    min_age = int(age_range.split("+")[0]) if "+" in age_range else None
                    if min_age and age >= min_age:
                        probability = adjusted_prob

            # Adjust probability based on gender
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

# Example usage
if __name__ == "__main__":
    # Example demographics data
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
        "household_size_distribution": [1, 2, 3, 4, 5, 6, 7],
        "household_size_probabilities": [0.3, 0.25, 0.2, 0.15, 0.05, 0.03, 0.02],
        "num_households": 50,
        "comorbidity_distribution": {
            "diabetes": {"base": 0.1, "age": {"40+": 0.2}},
            "hypertension": {"base": 0.15, "age": {"40+": 0.3}},
            "obesity": {"base": 0.2},
            "smoking": {"base": 0.25, "gender": {"male": 0.3, "female": 0.2}},
            "copd": {"base": 0.05, "age": {"50+": 0.1}},
            "chronic_heart_disease": {"base": 0.07, "age": {"50+": 0.15}},
            "chronic_kidney_disease": {"base": 0.03}
        }
    }

    # Generate synthetic population
    generator = SyntheticPopulationGenerator(demographics=demographics_data)
    households, population = generator.generate_population()

    # Print example households
