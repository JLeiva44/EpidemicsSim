from .disease_model import DiseaseModel
import random
class CovidModel(DiseaseModel):
    def __init__(self, transmission_rate, recovery_rate):
        """
        Model specific to COVID-19.

        :param transmission_rate: Probability of transmission per contact.
        :param recovery_rate: Probability of recovery per day.
        """
        states = ["susceptible", "infected", "recovered"]
        super().__init__(transmission_rate, recovery_rate, states)

    def update_states(self):
        """
        Update agent health states for COVID-19 (e.g., recovery or worsening).
        """
        for agent in self.agents:
            if agent.state == "infected":
                if random.random() < self.recovery_rate:
                    agent.state = "recovered"

    def _evaluate_transmission(self, agent1, agent2, duration):
        """
        Specific transmission logic for COVID-19.

        :param agent1: First agent in the interaction.
        :param agent2: Second agent in the interaction.
        :param duration: Duration of the contact.
        """
        if agent1.state == "infected" and agent2.state == "susceptible":
            if random.random() < self.transmission_rate * duration / 60:
                agent2.state = "infected"
        elif agent2.state == "infected" and agent1.state == "susceptible":
            if random.random() < self.transmission_rate * duration / 60:
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
