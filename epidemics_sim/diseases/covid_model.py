from .disease_model import DiseaseModel
import random



class CovidModel(DiseaseModel):
    def __init__(
        self, transmission_rate, incubation_period, asymptomatic_probability, base_mortality_rate,
        immunity_duration, recovery_rates, severity_durations, progression_rates
    ):
        # recovery_rates = {
        #     "asymptomatic": 0.99,
        #     "mild": 0.98,
        #     "moderate": 0.85,
        #     "severe": 0.6,
        #     "critical": 0.3,
        # }
        # severity_durations = {
        #     "mild": 7,
        #     "moderate": 14,
        #     "severe": 21,
        #     "critical": 28,
        # }
        super().__init__(
            "COVID-19",
            transmission_rate,
            incubation_period,
            asymptomatic_probability,
            base_mortality_rate,
            recovery_rates,
            severity_durations,
            immunity_duration,  # COVID-19: 90 días de inmunidad
        )

    def determine_severity(self, agent): # TODO: ver si el agente esta vacunado
        """
        Determine the severity of COVID-19 based on the agent's mortality rate.
        
        :param agent: The agent whose severity is being determined.
        :return: Severity level ('mild', 'moderate', 'severe', 'critical').
        """
        # Usamos la tasa de mortalidad del agente como referencia
        mortality = agent.mortality_rate  

        if mortality < 0.001:  # Bajo riesgo
            probabilities = [0.85, 0.12, 0.02, 0.01]  # Mayor probabilidad de síntomas leves
        elif mortality < 0.01:  # Riesgo moderado
            probabilities = [0.6, 0.25, 0.1, 0.05]  # Riesgo equilibrado
        elif mortality < 0.05:  # Riesgo alto
            probabilities = [0.4, 0.3, 0.2, 0.1]  # Más probabilidad de severidad
        else:  # Riesgo muy alto
            probabilities = [0.2, 0.3, 0.3, 0.2]  # Mayor probabilidad de estado crítico

        return random.choices(["mild", "moderate", "severe", "critical"], probabilities)[0]
