from .disease_model import DiseaseModel
import random

class DengueModel(DiseaseModel):
    def __init__(self, transmission_rate, recovery_rate):
        """
        Model specific to Dengue.

        :param transmission_rate: Probability of transmission per contact.
        :param recovery_rate: Probability of recovery per day.
        """
        states = ["susceptible", "infected", "immune"]
        super().__init__(transmission_rate, recovery_rate, states)

    def update_states(self):
        """
        Update agent health states for Dengue.
        """
        for agent in self.agents:
            if agent.state == "infected":
                if random.random() < self.recovery_rate:
                    agent.state = "immune"

    def _evaluate_transmission(self, agent1, agent2, duration):
        """
        Specific transmission logic for Dengue.

        :param agent1: First agent in the interaction.
        :param agent2: Second agent in the interaction.
        :param duration: Duration of the contact.
        """
        if agent1.state == "infected" and agent2.state == "susceptible":
            if random.random() < self.transmission_rate:
                agent2.state = "infected"
        elif agent2.state == "infected" and agent1.state == "susceptible":
            if random.random() < self.transmission_rate:
                agent1.state = "infected"


# class Dengue(BaseDisease):
#     def __init__(self):
#         """
#         Specific implementation for the Dengue disease.
#         """
#         super().__init__(
#             name="Dengue",
#             transmission_rate=0.02,  # Example value
#             recovery_rate=0.015,     # Example value
#             mortality_rate=0.002     # Example value
#         )

#     def __repr__(self):
#         return f"Dengue(name={self.name}, transmission_rate={self.transmission_rate}, recovery_rate={self.recovery_rate}, mortality_rate={self.mortality_rate})"
