from .disease_model import DiseaseModel
import random

class DengueModel(DiseaseModel):
    def __init__(self, agents, transmission_rate, recovery_rate, mortality_rate):
        """
        Model specific to Dengue.

        :param agents: List of agents in the simulation.
        :param transmission_rate: Probability of transmission per contact.
        :param recovery_rate: Probability of recovery per day.
        :param mortality_rate: Probability of death per day for infected agents.
        """
        states = ["susceptible", "infected", "immune", "deceased"]
        super().__init__(agents, transmission_rate, recovery_rate, mortality_rate, states)

    def update_states(self):
        """
        Update agent health states for Dengue, including mortality and immunity.
        """
        for agent in self.agents:
            if agent.state == "infected":
                # Evaluate mortality based on agent attributes
                mortality_chance = self.mortality_rate
                if agent.age > 50:  # Example factor: age threshold for Dengue
                    mortality_chance *= 1.4
                if "hypertension" in agent.comorbidities:
                    mortality_chance *= 1.2

                if random.random() < mortality_chance:
                    agent.state = "deceased"
                elif random.random() < self.recovery_rate:
                    agent.state = "immune"

    def _evaluate_transmission(self, agent1, agent2, duration):
        """
        Specific transmission logic for Dengue.

        :param agent1: First agent in the interaction.
        :param agent2: Second agent in the interaction.
        :param duration: Duration of the contact.
        """
        if agent1.state == "infected" and agent2.state == "susceptible" and not agent2.immune:
            transmission_probability = self.transmission_rate

            # Adjust based on contact duration
            transmission_probability *= duration / 60

            if random.random() < transmission_probability:
                agent2.state = "infected"
        elif agent2.state == "infected" and agent1.state == "susceptible" and not agent1.immune:
            transmission_probability = self.transmission_rate

            transmission_probability *= duration / 60

            if random.random() < transmission_probability:
                agent1.state = "infected"
