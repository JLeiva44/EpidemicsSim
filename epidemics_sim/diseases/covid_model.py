from .disease_model import DiseaseModel
import random

class CovidModel(DiseaseModel):
    def __init__(self, transmission_rate, incubation_period, asymptomatic_probability, base_mortality_rate):
        """
        Model specific to COVID-19.

        :param transmission_rate: Probability of transmission per contact.
        :param incubation_period: Number of days before symptoms or contagion begins.
        :param asymptomatic_probability: Probability of an agent being asymptomatic.
        :param base_mortality_rate: Base mortality rate for critical cases.
        """
        super().__init__("COVID-19", transmission_rate, incubation_period, asymptomatic_probability, base_mortality_rate)

    def determine_severity(self, agent):
        """
        COVID-19 specific severity determination considering comorbidities.

        :param agent: The agent whose severity is being determined.
        :return: Severity level ('mild', 'moderate', 'severe', 'critical').
        """
        probabilities = [0.6, 0.25, 0.1, 0.05]

        # Adjust probabilities based on comorbidities and age
        if agent.age_biological > 60:
            probabilities[2] += 0.05  # Increase severe probability
            probabilities[3] += 0.05  # Increase critical probability
        if "diabetes" in agent.comorbidities:
            probabilities[2] += 0.03
        if "obesity" in agent.comorbidities:
            probabilities[1] += 0.03
        if "hypertension" in agent.comorbidities:
            probabilities[2] += 0.02
        if "cancer" in agent.comorbidities:
            probabilities[3] += 0.04

        return random.choices(["mild", "moderate", "severe", "critical"], probabilities)[0]
