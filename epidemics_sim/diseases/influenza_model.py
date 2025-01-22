from .disease_model import DiseaseModel
import random

class InfluenzaModel(DiseaseModel):
    def __init__(self, transmission_rate, recovery_rate, mortality_rate):
        """
        Model specific to Influenza.

        :param transmission_rate: Probability of transmission per contact.
        :param recovery_rate: Probability of recovery per day.
        :param mortality_rate: Probability of death if in critical condition.
        """
        super().__init__(transmission_rate, recovery_rate, mortality_rate)

    def calculate_transmission_probability(self, source, target):
        """
        Calculate Influenza specific transmission probability.

        :param source: Source agent.
        :param target: Target agent.
        :return: Transmission probability.
        """
        transmission_probability = self.transmission_rate

        # Adjust for vaccination status
        if target.vaccinated:
            transmission_probability *= 0.6

        return transmission_probability

    def determine_severity(self, agent):
        """
        Influenza-specific severity determination considering age groups.

        :param agent: The agent whose severity is being determined.
        :return: Severity level ('mild', 'moderate', 'severe', 'critical').
        """
        severity_levels = ["mild", "moderate", "severe", "critical"]
        probabilities = [0.7, 0.2, 0.08, 0.02]

        # Adjust probabilities for high-risk groups
        if agent.age < 5 or agent.age > 65:
            probabilities[2] += 0.02  # Increase severe probability
            probabilities[3] += 0.02  # Increase critical probability

        return random.choices(severity_levels, probabilities)[0]
