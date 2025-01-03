from .disease_model import DiseaseModel
import random
class CovidModel(DiseaseModel):
    def __init__(self, agents, transmission_rate, recovery_rate, mortality_rate):
        """
        Model specific to COVID-19.

        :param agents: List of agents in the simulation.
        :param transmission_rate: Probability of transmission per contact.
        :param recovery_rate: Probability of recovery per day.
        :param mortality_rate: Probability of death per day for infected agents.
        """
        states = ["susceptible", "infected", "recovered", "deceased"]
        super().__init__(agents, transmission_rate, recovery_rate, mortality_rate, states)

    def update_states(self):
        """
        Update agent health states for COVID-19, including mortality and recovery.
        """
        for agent in self.agents:
            if agent.state == "infected":
                # Evaluate mortality based on agent attributes
                mortality_chance = self.mortality_rate
                if agent.age > 60:  # Example factor: age
                    mortality_chance *= 1.5
                if "diabetes" in agent.comorbidities:
                    mortality_chance *= 1.3

                if random.random() < mortality_chance:
                    agent.state = "deceased"
                elif random.random() < self.recovery_rate:
                    agent.state = "recovered"
                    agent.immune = True

    def _evaluate_transmission(self, agent1, agent2, duration):
        """
        Evaluate transmission between two agents based on their states, vaccination, and mask usage.
        """
        if agent1.state == "infected" and agent2.state == "susceptible" and not agent2.immune:
            transmission_probability = self.transmission_rate

            # Adjust for vaccination and mask usage
            if agent2.vaccinated:
                transmission_probability *= 0.5  # Example: 50% reduction
            if agent2.mask_usage or agent1.mask_usage:
                transmission_probability *= 0.7  # Example: 30% reduction

            # Adjust based on contact duration
            transmission_probability *= duration / 60

            if random.random() < transmission_probability:
                agent2.state = "infected"
        elif agent2.state == "infected" and agent1.state == "susceptible" and not agent1.immune:
            transmission_probability = self.transmission_rate

            if agent1.vaccinated:
                transmission_probability *= 0.5
            if agent2.mask_usage or agent1.mask_usage:
                transmission_probability *= 0.7

            transmission_probability *= duration / 60

            if random.random() < transmission_probability:
                agent1.state = "infected"


# class Covid(BaseDisease):
#     def __init__(self):
#         """
#         Specific implementation for the COVID-19 disease.
#         """
#         super().__init__(
#             name="COVID-19",
#             transmission_rate=0.03,  # Example value
#             recovery_rate=0.01,      # Example value
#             mortality_rate=0.005     # Example value
#         )

#     def __repr__(self):
#         return f"Covid(name={self.name}, transmission_rate={self.transmission_rate}, recovery_rate={self.recovery_rate}, mortality_rate={self.mortality_rate})"
