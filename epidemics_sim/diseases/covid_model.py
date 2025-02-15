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
            immunity_duration,  # COVID-19: 90 días de inmunidad
            recovery_rates,
            severity_durations,
            progression_rates
        )

    import random

    def determine_severity(self, agent):
        """
        Determina la severidad del COVID-19 en un agente basado en su tasa de mortalidad basal ajustada.

        :param agent: Instancia del agente.
        :return: Nivel de severidad ('mild', 'moderate', 'severe', 'critical').
        """
        mortality = agent.mortality_rate  # Tasa de mortalidad ajustada por edad y comorbilidades

        if mortality < 0.0001:  # Muy bajo riesgo (jóvenes sin comorbilidades)
            probabilities = [0.90, 0.08, 0.015, 0.005]  
        elif mortality < 0.001:  # Bajo riesgo (adultos jóvenes o sin comorbilidades)
            probabilities = [0.80, 0.15, 0.04, 0.01]  
        elif mortality < 0.005:  # Riesgo moderado (adultos con comorbilidades leves)
            probabilities = [0.65, 0.20, 0.10, 0.05]  
        elif mortality < 0.02:  # Riesgo alto (mayores de 50 o con varias comorbilidades)
            probabilities = [0.50, 0.25, 0.15, 0.10]  
        else:  # Riesgo crítico (mayores de 70 o con enfermedades graves)
            probabilities = [0.30, 0.30, 0.25, 0.15]  

        # Si el agente está vacunado, reducimos la probabilidad de los casos severos
        if agent.vaccinated:
            reduction_factor = agent.vaccine_effectiveness  # Ej: 0.8 reduce en 80% los casos graves
            probabilities[2] *= (1 - reduction_factor)  # Reducir síntomas severos
            probabilities[3] *= (1 - reduction_factor)  # Reducir síntomas críticos

            # Reajustar probabilidades para que sumen 1
            total = sum(probabilities)
            probabilities = [p / total for p in probabilities]

        return random.choices(["mild", "moderate", "severe", "critical"], probabilities)[0]

    # def determine_severity(self, agent): # TODO: ver si el agente esta vacunado
    #     """
    #     Determine the severity of COVID-19 based on the agent's mortality rate.
        
    #     :param agent: The agent whose severity is being determined.
    #     :return: Severity level ('mild', 'moderate', 'severe', 'critical').
    #     """
    #     # Usamos la tasa de mortalidad del agente como referencia
    #     mortality = agent.mortality_rate  

    #     if mortality < 0.001:  # Bajo riesgo
    #         probabilities = [0.85, 0.12, 0.02, 0.01]  # Mayor probabilidad de síntomas leves
    #     elif mortality < 0.01:  # Riesgo moderado
    #         probabilities = [0.6, 0.25, 0.1, 0.05]  # Riesgo equilibrado
    #     elif mortality < 0.05:  # Riesgo alto
    #         probabilities = [0.4, 0.3, 0.2, 0.1]  # Más probabilidad de severidad
    #     else:  # Riesgo muy alto
    #         probabilities = [0.2, 0.3, 0.3, 0.2]  # Mayor probabilidad de estado crítico

    #     if agent.vaccinated:
    #         probabilities[2] *= agent.vaccine_effectiveness  # Reducir probabilidad de síntomas moderados
    #         probabilities[3] *= agent.vaccine_effectiveness  # Reducir probabilidad de síntomas graves
    #         probabilities[4] *= agent.vaccine_effectiveness  # Reducir probabilidad de síntomas críticos    

    #     return random.choices(["mild", "moderate", "severe", "critical"], probabilities)[0]
