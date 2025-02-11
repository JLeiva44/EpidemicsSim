import random
from abc import ABC, abstractmethod
from epidemics_sim.agents.base_agent import State
import math
class DiseaseModel(ABC):
    def __init__(
        self,
        name,
        transmission_rate,
        incubation_period,
        asymptomatic_probability,
        base_mortality_rate,
        recovery_rates,
        severity_durations,
        immunity_duration=0,  # Nueva variable: define duración de la inmunidad
    ):
        """
        Base class for diseases transmitted by contact.

        :param name: Name of the disease (e.g., "COVID-19").
        :param transmission_rate: Probability of transmission per contact.
        :param incubation_period: Number of days before symptoms or contagion begins.
        :param asymptomatic_probability: Probability of an agent being asymptomatic.
        :param base_mortality_rate: Base mortality rate for critical cases.
        :param recovery_rates: Dictionary of recovery rates by severity.
        :param severity_durations: Dictionary of durations by severity.
        :param immunity_duration: Number of days agents remain immune after recovery (0 = no immunity).
        """
        self.name = name
        self.transmission_rate = transmission_rate
        print(f"El rate de trasnmision es " ,self.transmission_rate)
        self.incubation_period = incubation_period
        self.asymptomatic_probability = asymptomatic_probability
        self.base_mortality_rate = base_mortality_rate
        self.recovery_rates = recovery_rates
        self.severity_durations = severity_durations
        self.immunity_duration = immunity_duration  # Guardamos el tiempo de inmunidad

    
    def initialize_infections(self, agents):
        """
        Infect a set of agents initially.

        :param agents: List of agents to infect.
        """
        for agent in agents:
            agent.transition(State.INFECTED, reason=f"Initial {self.name} infection")
            agent.days_infected = 0
            agent.infection_status = {
                "disease": self.name,
                "state": State.INFECTED,
                "severity": None,
                "contagious": False,  
                "days_infected": 0,
                "asymptomatic": random.random() < self.asymptomatic_probability,
            }

    def propagate(self, daily_interactions):
        """
        Handle the propagation of the disease based on daily interactions.

        :param daily_interactions: Dictionary of daily interactions by time intervals.
        """
        for time_period, interactions in daily_interactions.items():
            for agent1, agent2 in interactions:  # Each interaction is a tuple (agent1, agent2)
                
                if agent1.is_isolated or agent2.is_isolated or agent1.is_hospitalized or agent2.is_hospitalized:
                    print("Estan llegando agentes isolados u hospitalizados a la propagacion")
                # Aqui no deben llegar agentes isolados u hospitalizados porque los quito de las interaciones en simulate_day
                if (agent1.infection_status["state"] == State.INFECTED or agent2.infection_status["state"] == State.INFECTED):
                    self._evaluate_transmission((agent1, agent2))

        a = 6 # Debugging 
        b = 9 # Debugging           

    def _evaluate_transmission(self, interaction):
        """
        Evaluate transmission between two agents.

        :param interaction: Tuple (agent1, agent2).
        """
        agent1, agent2 = interaction
        if agent1.infection_status["contagious"]:
            self._attempt_infection(agent1, agent2)
        if agent2.infection_status["contagious"]:
            self._attempt_infection(agent2, agent1)

    def _attempt_infection(self, source, target):
        """
        Attempt to infect the target agent from the source agent.

        :param source: Source agent.
        :param target: Target agent.
        """
        if target.infection_status["state"] is State.SUSCEPTIBLE and not target.immune:
            transmission_probability = self.calculate_transmission_probability(source, target)
            if random.random() < transmission_probability:
                target.transition(State.INFECTED, reason=f"Infected by {self.name}")
                target.infection_status.update({
                    "disease": self.name,
                    "state": State.INFECTED,
                    "contagious": False,
                    "severity": None,
                    "days_infected": 0,
                    "asymptomatic": random.random() < self.asymptomatic_probability,
                    "immunity_days": self.immunity_duration
                })
                #print(target.municipio)

    def calculate_transmission_probability(self, source, target):
        """
        Calculate the transmission probability specific to the disease.

        :param source: Source agent.
        :param target: Target agent.
        :return: Transmission probability.
        """
        probability = self.transmission_rate

        # Adjust for vaccination status
        if target.vaccinated:
            probability = (1 - target.vaccine_effectiveness)

        source_mask_factor = source.mask.get("reduction_factor", 1.0) if source.mask.get("usage", False) else 1.0
        target_mask_factor = target.mask.get("reduction_factor", 1.0) if target.mask.get("usage", False) else 1.0

        probability *= source_mask_factor * target_mask_factor  # Se multiplica el efecto de ambas mascarillas
        return probability



    def progress_infection(self, agent):
        """
        Progress the infection state for the given agent.

        :param agent: The agent whose infection state is being progressed.
        """
        if agent.infection_status["days_infected"] == 0:
            agent.incubation_period = self.incubation_period()

        agent.infection_status["days_infected"] += 1
        days_infected = agent.infection_status["days_infected"]

        # 1️⃣ INCUBACIÓN: No síntomas ni transmisión hasta que termine
        if days_infected <= agent.incubation_period:
            agent.infection_status["contagious"] = False
            return

        # 2️⃣ FIN DE INCUBACIÓN: Definir severidad y contagiosidad
        if days_infected == agent.incubation_period + 1:
            agent.infection_status["contagious"] = True  # Ahora puede contagiar
            if agent.infection_status["asymptomatic"]:
                agent.infection_status.update({
                    "severity": "asymptomatic",
                    "state": State.INFECTED
                })
                agent.transition(State.INFECTED, reason=f"{self.name} infection")
            else:
                severity = self.determine_severity(agent)
                agent.infection_status.update({
                    "severity": severity,
                    "state": State.INFECTED
                })
                agent.transition(State.INFECTED, reason=f"{self.name} infection ({severity})")
            return

        severity = None
        recovery_days = None
        # 3️⃣ PROGRESIÓN: Evaluar cambio de gravedad
        if not agent.infection_status["severity"] == "asymptomatic":
            severity = agent.infection_status.get("severity", "mild")
            recovery_days = self.severity_durations.get(severity, 10)  # Tiempo base de recuperación

        elif agent.infection_status["severity"] == "asymptomatic":
            recovery_days = random.uniform(5, 10)  # Recuperación más rápida

        # 💡 Bonus de recuperación si está hospitalizado
        recovery_bonus = 1.3 if agent.is_hospitalized else 1.0  

        # Probabilidad base de progresión según severidad
        progression_rates = {
            "asymptomatic": 0,
            "mild": 0.15,        # 15% de pasar a moderado
            "moderate": 0.25,    # 25% de pasar a severo
            "severe": 0.40,      # 40% de pasar a crítico
        }

        # Obtener la mortalidad ajustada del agente
        mortality_risk = self.calculate_critical_mortality_rate(agent.mortality_rate)

        # 📌 **Nueva Fórmula**: Probabilidad combinada usando logaritmo
        progression_probability = progression_rates.get(severity, 0) * math.log(1 + agent.mortality_rate * 10)

        # Evaluar si el paciente empeora
        if severity in progression_rates and random.random() < progression_probability:
            new_severity = {
                "mild": "moderate",
                "moderate": "severe",
                "severe": "critical"
            }[severity] # TODO : Esto debe ser independiente para cada enfermedad y con datos esepcificos
            agent.infection_status.update({"severity": new_severity})
            agent.transition(State.INFECTED, reason=f"{self.name} worsened to {new_severity}")
            return

        # 4️⃣ Evaluar recuperación o muerte
        if days_infected >= agent.incubation_period + recovery_days:
            # 🚨 CASOS CRÍTICOS: Posibilidad de muerte
            if severity == "critical" and random.random() < (mortality_risk / recovery_bonus):
                agent.infection_status.update({
                    "state": State.DECEASED,
                    "contagious": False,
                    "severity": "critical"
                })
                agent.transition(State.DECEASED, reason=f"{self.name} critical condition")
                return  # 🚨 Agente murió, no sigue en la simulación

            # ✅ RECUPERACIÓN: Puede ser inmune o volver a ser susceptible
            if random.random() < (self.recovery_rates.get(severity, 1.0) * recovery_bonus):
                agent.infection_status.update({
                    "state": State.RECOVERED,
                    "contagious": False,
                    "severity": None,
                    "days_infected": 0,
                })
                agent.transition(State.RECOVERED, reason=f"{self.name} recovery")

                # 3.3️⃣ ¿La inmunidad es temporal?
                if self.immunity_duration > 0:
                    agent.infection_status["immunity_days"] = self.immunity_duration
                else:
                    agent.infection_status["immunity_days"] = 0
                return

        # 5️⃣ REINFECCIÓN: Si la inmunidad es temporal, vuelve a ser susceptible
        if agent.infection_status["state"] == State.RECOVERED and "immunity_days" in agent.infection_status:
            agent.infection_status["immunity_days"] -= 1
            if agent.infection_status["immunity_days"] <= 0:
                agent.infection_status.update({
                    "state": State.SUSCEPTIBLE,
                    "disease": "",
                    "severity": None,
                    "contagious": False,
                    "days_infected": 0,
                    "asymptomatic": None,
                    "immunity_days": 0
                })
                agent.transition(State.SUSCEPTIBLE, reason=f"{self.name} immunity waned")
                agent.immune = False  

    # def progress_infection(self, agent):
    #     """
    #     Progress the infection state for the given agent.

    #     :param agent: The agent whose infection state is being progressed.
    #     """
    #     if agent.infection_status["days_infected"] == 0:
    #         agent.incubation_period = self.incubation_period()

    #     agent.infection_status["days_infected"] += 1
    #     days_infected = agent.infection_status["days_infected"]

    #     # 1️⃣ INCUBACIÓN: No síntomas ni transmisión hasta que termine
    #     if days_infected <= agent.incubation_period:
    #         agent.infection_status["contagious"] = False
    #         return

    #     # 2️⃣ FIN DE INCUBACIÓN: Definir severidad y contagiosidad
    #     if days_infected == agent.incubation_period + 1:
    #         agent.infection_status["contagious"] = True  # Ya puede contagiar
    #         if agent.infection_status["asymptomatic"]:
    #             agent.infection_status.update({
    #                 "severity": "asymptomatic",
    #                 "state": State.INFECTED
    #             })
    #             agent.transition(State.INFECTED, reason=f"{self.name} infection")
    #         else: # Si es asintomatico no se le determina la severidad
    #             severity = self.determine_severity(agent)
    #             agent.infection_status.update({
    #                 "severity": severity,
    #                 "state": State.INFECTED
    #             })
    #             agent.transition(State.INFECTED, reason=f"{self.name} infection ({severity})")
    #         return

    #     # 3️⃣ PROGRESIÓN: Evaluar recuperación o muerte
    #     severity = agent.infection_status.get("severity", "mild")
    #     recovery_days = self.severity_durations.get(severity, 10)  # Tiempo de recuperación

    #     if days_infected >= agent.incubation_period + recovery_days:
    #         # 3.1️⃣ CASOS CRÍTICOS: Posibilidad de muerte
    #         if severity == "critical" and random.random() < agent.update_mortality_rate(self.base_mortality_rate):
    #             agent.infection_status.update({
    #                 "state": State.DECEASED,
    #                 "contagious": False,
    #                 "severity": "critical"
    #             })
    #             agent.transition(State.DECEASED, reason=f"{self.name} critical condition")
    #             return  # 🚨 Agente murió, no sigue en la simulación

    #         # 3.2️⃣ RECUPERACIÓN: Puede ser inmune o volver a ser susceptible
    #         if random.random() < self.recovery_rates.get(severity, 1.0):
    #             agent.infection_status.update({
    #                 "state": State.RECOVERED,
    #                 "contagious": False,
    #                 "severity": None,
    #                 "days_infected": 0,
    #             })
    #             agent.transition(State.RECOVERED, reason=f"{self.name} recovery")

    #             # 3.3️⃣ ¿La inmunidad es temporal?
    #             if self.immunity_duration > 0:
    #                 agent.infection_status["immunity_days"] = self.immunity_duration
    #             else:
    #                 agent.infection_status["immunity_days"] = 0
    #             return

    #     # 4️⃣ REINFECCIÓN: Si la inmunidad es temporal, vuelve a ser susceptible
    #     if agent.infection_status["state"] == State.RECOVERED and "immunity_days" in agent.infection_status:
    #         agent.infection_status["immunity_days"] -= 1
    #         if agent.infection_status["immunity_days"] <= 0:
    #             agent.infection_status.update({
    #                 "state": State.SUSCEPTIBLE,
    #                 "disease": "",
    #                 "severity": None,
    #                 "contagious": False,
    #                 "days_infected": 0,
    #                 "asymptomatic": None,
    #                 "immunity_days": 0
    #             })
    #             agent.transition(State.SUSCEPTIBLE, reason=f"{self.name} immunity waned")
    #             agent.immune = False  
  
    def calculate_critical_mortality_rate(self, agent_mortality_rate):
        """
        Update the agent's mortality rate based on base mortality and disease mortality rates.

        :param disease_mortality_rate: Disease-specific mortality rate (0 to 1).
        :param vaccine_efficacy: Reduction in mortality due to vaccination (0 to 1). Default is 0 (no vaccination).
        """
        # Combine using the log-based formula
        combined_rate = 1 - (1 - agent_mortality_rate) * (1 - self.base_mortality_rate)

        # # Apply vaccine efficacy if vaccinated
        # if self.vaccinated:
        #     combined_rate *= (1 - vaccine_efficacy)

        #self.mortality_rate = combined_rate
        return combined_rate

                
    @abstractmethod
    def determine_severity(self, agent):
        """
        Determine the severity of the disease for an agent.

        :param agent: The agent whose severity is being determined.
        :return: Severity level ('mild', 'moderate', 'severe', 'critical').
        """
        pass
