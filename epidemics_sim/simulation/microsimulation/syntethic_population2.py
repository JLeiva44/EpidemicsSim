from epidemics_sim.agents.human_agent import HumanAgent
import random

class SyntheticPopulationGenerator:
    def __init__(self, num_agents, demographics):
        """
        Class to generate a synthetic population.

        :param num_agents: Total number of agents to generate.
        :param demographics: Dictionary with demographic data (e.g., age distribution, gender ratio).
        """
        self.num_agents = num_agents
        self.demographics = demographics

    #TODO: Use demographics to generate agents with attributes
    def generate_population(self):
        """
        Generate a population of agents with demographic attributes.

        :return: List of agents with attributes.
        """

        agents = self._generate_agents()
        
        households = self._generate_households(agents)

        return households,agents


    def _generate_agents(self):
        agents = []
        for agent_id in range(self.num_agents):
            age = self._generate_age()
            gender = random.choice(["male", "female"])
            occupation = self._generate_ocupation()
            comorbidities = self._generate_comorbidities()

            agent = HumanAgent(agent_id, None,age,gender, occupation,None,comorbidities, None, None)
            
    
            agents.append(agent)
        return agents


    def _generate_households(self, agents):
        """
        Generate households ensuring each has at least one member aged 18 or older.

        :return: A list of households with agents.
        """
        import random

        # Example: Household size distribution (percentages for each household size)
        household_sizes = [1, 2, 3, 4, 5, 6, 7]
        size_probabilities = [0.3, 0.25, 0.2, 0.15, 0.05, 0.03, 0.02]

        households = []
        unassigned_agents = agents.copy()

        while unassigned_agents:
            size = random.choices(household_sizes, size_probabilities)[0]

            # Ensure there are enough agents left to form a household
            if len(unassigned_agents) < size:
                size = len(unassigned_agents)

            # Select agents for the household
            household = unassigned_agents[:size]

            # Check if there's at least one adult (age >= 18)
            if not any(agent["age"] >= 18 for agent in household):
                # Add one adult if available
                adults = [agent for agent in unassigned_agents if agent["age"] >= 18]
                if adults:
                    household[-1] = adults[0]
                    unassigned_agents.remove(adults[0])

            # Assign household ID and remove agents from the unassigned list
            household_id = household[0]["id"]
            for agent in household:
                agent["household_id"] = household_id
            households.append(household)
            unassigned_agents = [agent for agent in unassigned_agents if agent not in household]

        return households


    
    
    def _generate_comorbidities(self):
        """
        Generate comorbidities based on the demographics distribution.

        :return: A list of comorbidities for an agent.
        """
        import random

        # Example: Comorbidity distribution (percentages for each comorbidity)
        comorbidity_distribution = { #TODO Ver los datos cubanos
            "diabetes": 0.1,
            "hypertension": 0.15,
            "obesity": 0.2,
            "smoking": 0.25,
            "copd": 0.05,
            "chronic_heart_disease": 0.07,
            "chronic_kidney_disease": 0.03
        }

        comorbidities = {}
        for comorbidity, probability in comorbidity_distribution.items():
            if random.random() < probability:
                comorbidities[comorbidity] = True
        return comorbidities  
    
    
    def _generate_ocupation(self): # Worker or Student based on demographics
        pass
        

    def _generate_age(self):
        """
        Generate an age based on the demographics distribution.

        :return: An integer representing the age of an agent.
        """
        import random

        # Example: Age distribution (percentages for age ranges)
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

    # def _assign_morbidities(self, agents):
    #     """
    #     Assign morbidities to agents based on probabilities.

    #     :param agents: List of agents to assign morbidities to.
    #     """
    #     import random

    #     for agent in agents:
    #         age = agent["age"]
    #         morbidities = {
    #             "diabetes": random.random() < 0.1 if age > 40 else 0.02,
    #             "hypertension": random.random() < 0.15 if age > 40 else 0.05,
    #             "obesity": random.random() < 0.2,
    #             "smoking": random.random() < 0.25,
    #             "copd": random.random() < 0.05 if age > 50 else 0.01,
    #             "chronic_heart_disease": random.random() < 0.07 if age > 50 else 0.02,
    #             "chronic_kidney_disease": random.random() < 0.03
    #         }
    #         agent["attributes"].update(morbidities)

