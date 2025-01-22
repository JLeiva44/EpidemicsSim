from .disease_model import DiseaseModel
import random
from .disease_model import DiseaseModel
import random
class CovidModel(DiseaseModel):
    def __init__(self, transmission_rate, recovery_rate, mortality_rate):
        """
        Model specific to COVID-19.

        :param transmission_rate: Probability of transmission per contact.
        :param recovery_rate: Probability of recovery per day.
        :param mortality_rate: Probability of death if in critical condition.
        """
        super().__init__(transmission_rate, recovery_rate, mortality_rate)

    def calculate_transmission_probability(self, source, target):
        """
        Calculate COVID-19 specific transmission probability.

        :param source: Source agent.
        :param target: Target agent.
        :return: Transmission probability.
        """
        transmission_probability = self.transmission_rate

        # Adjust for mask usage
        if source.mask_usage or target.mask_usage:
            transmission_probability *= 0.7

        # Adjust for vaccination status
        if target.vaccinated:
            transmission_probability *= 0.5

        return transmission_probability

    def determine_severity(self, agent):
        """
        COVID-19 specific severity determination considering comorbidities.

        :param agent: The agent whose severity is being determined.
        :return: Severity level ('mild', 'moderate', 'severe', 'critical').
        """
        severity_levels = ["mild", "moderate", "severe", "critical"]
        probabilities = [0.8, 0.15, 0.04, 0.01]

        # Adjust probabilities based on comorbidities
        if "diabetes" in agent.comorbidities:
            probabilities[2] += 0.02
        if "obesity" in agent.comorbidities:
            probabilities[1] += 0.03
        if "hypertension" in agent.comorbidities:
            probabilities[2] += 0.03
        if agent.age > 60:
            probabilities[3] += 0.03

        return random.choices(severity_levels, probabilities)[0]