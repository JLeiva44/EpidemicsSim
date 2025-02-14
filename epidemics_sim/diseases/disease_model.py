import random
from abc import ABC, abstractmethod
from epidemics_sim.agents.base_agent import State
import math
from epidemics_sim.simulation.logger import setup_logger
logger = setup_logger()
class DiseaseModel(ABC):
    def __init__(
        self,
        name,
        transmission_rate,
        mean_incubation_period,
        asymptomatic_probability,
        base_mortality_rate,
        immunity_duration,  # Nueva variable: define duración de la inmunidad
        recovery_rates,
        severity_durations,
        progresion_rates,
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
        self.mean_incubation_period = mean_incubation_period
        self.asymptomatic_probability = asymptomatic_probability
        self.base_mortality_rate = base_mortality_rate
        self.recovery_rates = recovery_rates
        self.severity_durations = severity_durations
        self.immunity_duration = immunity_duration  # Guardamos el tiempo de inmunidad
        self.progression_rates = progresion_rates

    
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

    def propagate(self, daily_interactions, agents):
        """
        Handle the propagation of the disease based on daily interactions.

        :param daily_interactions: Dictionary of daily interactions by time intervals.
        """
        print("Propagando enfermedad")
        count_interaction = 0
        count_evaluation = 0
        new = {}
        for time_period, interactions in daily_interactions.items():
            for id1, id2 in interactions:  # Each interaction is a tuple (agent1, agent2)
                count_interaction += 1
                if agents[id1].is_isolated or agents[id2].is_isolated or agents[id1].is_hospitalized or agents[id2].is_hospitalized:
                    print("Estan llegando agentes isolados u hospitalizados a la propagacion")
                # Aqui no deben llegar agentes isolados u hospitalizados porque los quito de las interaciones en simulate_day
                #logger.info("Agentes que se infestaron dentro de propagate")
                if agents[id1].infection_status["state"] is State.INFECTED and agents[id1].infection_status["contagious"] and agents[id2].infection_status["state"] is State.SUSCEPTIBLE and not agents[id2].immune:
                    transmission_probability = self.calculate_transmission_probability(id1, id2,agents)
                    if random.random() < transmission_probability:
                        count_evaluation += 1
                        agents[id2].transition(State.INFECTED, reason=f"Infected by {self.name}")
                        agents[id2].infection_status["disease"] = self.name
                        agents[id2].infection_status["state"] = State.INFECTED
                        agents[id2].infection_status["contagious"] = False
                        agents[id2].infection_status["severity"] = None
                        agents[id2].infection_status["days_infected"] = 0
                        agents[id2].infection_status["asymptomatic"] = random.random() < self.asymptomatic_probability
                        agents[id2].infection_status["immunity_days"] = self.immunity_duration
                        new[count_evaluation] = agents[id2]
                        #logger.debug(f"Infestado el agente {id2}")
                
                if agents[id2].infection_status["state"] is State.INFECTED and agents[id2].infection_status["contagious"] and agents[id1].infection_status["state"] is State.SUSCEPTIBLE and not agents[id1].immune:
                    transmission_probability = self.calculate_transmission_probability(id2, id1,agents) 
                    if random.random() < transmission_probability:
                        count_evaluation += 1
                        agents[id1].transition(State.INFECTED, reason=f"Infected by {self.name}")
                        agents[id1].infection_status["disease"] = self.name
                        agents[id1].infection_status["state"] = State.INFECTED
                        agents[id1].infection_status["contagious"] = True
                        agents[id1].infection_status["severity"] = None
                        agents[id1].infection_status["days_infected"] = 0
                        agents[id1].infection_status["asymptomatic"] = random.random() < self.asymptomatic_probability
                        agents[id1].infection_status["immunity_days"] = self.immunity_duration
                        new[count_evaluation] = agents[id1]
                        #logger.debug(f"Infestado el agente {id1}")
                
                # if (agents[id1].infection_status["state"] is State.INFECTED or agents[id2].infection_status["state"] is State.INFECTED):
                #     count_evaluation += 1
                #     new[count_evaluation] = self._evaluate_transmission((id1, id2), agents)

        #logger.debug("............................................................")
        return new
        
                

    # def _evaluate_transmission(self, interaction, agents):
    #     """
    #     Evaluate transmission between two agents.

    #     :param interaction: Tuple (agent1, agent2).
    #     """
    #     agent1, agent2 = interaction
    #     if agents[agent1].infection_status["contagious"] and agents[agent2].infection_status["state"] is State.SUSCEPTIBLE:
    #         return self._attempt_infection(agent1, agent2, agents)
    #     if agents[agent2].infection_status["contagious"] and agents[agent1].infection_status["state"] is State.SUSCEPTIBLE:
    #         return self._attempt_infection(agent2, agent1, agents)

    # def _attempt_infection(self, source, target, agents):
    #     """
    #     Attempt to infect the target agent from the source agent.

    #     :param source: Source agent.
    #     :param target: Target agent.
    #     """
    #     count_attempt = 0 
    #     count_good = 0
    #     print("Intentando infectar")
    #     if agents[target].infection_status["state"] is State.SUSCEPTIBLE and not agents[target].immune:
    #         transmission_probability = self.calculate_transmission_probability(source, target,agents)
    #         print(f"probabilidad de transmision {transmission_probability}")
    #         count_attempt += 1
    #         if random.random() < transmission_probability:
    #             count_good +=1
    #             agents[target].transition(State.INFECTED, reason=f"Infected by {self.name}")
    #             agents[target].infection_status["disase"] = self.name
    #             agents[target].infection_status["state"] = State.INFECTED
    #             agents[target].infection_status["contagious"] = True
    #             agents[target].infection_status["severity"] = None
    #             agents[target].infection_status["days_infected"] = 0
    #             agents[target].infection_status["asymptomatic"] = random.random() < self.asymptomatic_probability
    #             agents[target].infection_status["immunity_days"] = self.immunity_duration
    #             # agents[target].infection_status.update({
    #             #     "disease": self.name,
    #             #     "state": State.INFECTED,
    #             #     "contagious": True,
    #             #     "severity": None,
    #             #     "days_infected": 0,
    #             #     "asymptomatic": random.random() < self.asymptomatic_probability,
    #             #     "immunity_days": self.immunity_duration
    #             # })
    #             #print(target.municipio)
    #             return agents[target]  

    #     #print(f"Intentos de infeccion {count_attempt} y exitosos {count_good}")        

    def calculate_transmission_probability(self, source, target, agents):
        """
        Calculate the transmission probability specific to the disease.

        :param source: Source agent.
        :param target: Target agent.
        :return: Transmission probability.
        """
        probability = self.transmission_rate

        # Adjust for vaccination status
        if agents[target].vaccinated:
            probability = (1 - target.vaccine_effectiveness)

        source_mask_factor = agents[source].mask.get("reduction_factor", 1.0) if agents[source].mask.get("usage", False) else 1.0
        target_mask_factor = agents[target].mask.get("reduction_factor", 1.0) if agents[target].mask.get("usage", False) else 1.0

        probability *= source_mask_factor * target_mask_factor  # Se multiplica el efecto de ambas mascarillas
        return probability



    def progress_infection(self, agent, agents):
        """
        Progress the infection state for the given agent.

        :param agent: The agent whose infection state is being progressed.
        """
        if agents[agent].infection_status["days_infected"] == 0:
            # incubation_period = random.gauss(self.mean_incubation_period[0], self.mean_incubation_period[1])
            incubation_period = round(random.gauss(self.mean_incubation_period[0], self.mean_incubation_period[1]))
            agents[agent].incubation_period = max(incubation_period, 0)

        agents[agent].infection_status["days_infected"] += 1
        days_infected = agents[agent].infection_status["days_infected"]

        # 1️⃣ INCUBACIÓN: No síntomas ni transmisión hasta que termine
        if days_infected <= agents[agent].incubation_period:
            agents[agent].infection_status["contagious"] = False
            return

        # 2️⃣ FIN DE INCUBACIÓN: Definir severidad y contagiosidad
        if days_infected == agents[agent].incubation_period + 1:
            agents[agent].infection_status["contagious"] = True  # Ahora puede contagiar
            if agents[agent].infection_status["asymptomatic"]:
                agents[agent].infection_status.update({
                    "severity": "asymptomatic",
                    "state": State.INFECTED
                })
                agents[agent].transition(State.INFECTED, reason=f"{self.name} infection")
            else:
                severity = self.determine_severity(agents[agent])
                agents[agent].infection_status.update({
                    "severity": severity,
                    "state": State.INFECTED
                })
                agents[agent].transition(State.INFECTED, reason=f"{self.name} infection ({severity})")
            return

        severity = None
        recovery_days = None
        # 3️⃣ PROGRESIÓN: Evaluar cambio de gravedad
        if not agents[agent].infection_status["severity"] == "asymptomatic":
            severity = agents[agent].infection_status.get("severity", "mild")
            recovery_days = self.severity_durations.get(severity, 10)  # Tiempo base de recuperación

        elif agents[agent].infection_status["severity"] == "asymptomatic":
            recovery_days = random.randint(5, 10)  # Recuperación más rápida

        # 💡 Bonus de recuperación si está hospitalizado
        recovery_bonus = 1.3 if agents[agent].is_hospitalized else 1.0  

        # Probabilidad base de progresión según severidad
        # progression_rates = {
        #     "asymptomatic": 0,
        #     "mild": 0.15,        # 15% de pasar a moderado
        #     "moderate": 0.25,    # 25% de pasar a severo
        #     "severe": 0.40,      # 40% de pasar a crítico
        # }

        # Obtener la mortalidad ajustada del agents[agent]e
        mortality_risk = self.calculate_critical_mortality_rate(agents[agent].mortality_rate)

        # 📌 **Nueva Fórmula**: Probabilidad combinada usando logaritmo
        progression_probability = self.progression_rates.get(severity, 0) * math.log(1 + agents[agent].mortality_rate * 10)

        # Evaluar si el paciente empeora
        if severity in self.progression_rates and random.random() < progression_probability:
            new_severity = {
                "mild": "moderate",
                "moderate": "severe",
                "severe": "critical"
            }[severity] # TODO : Esto debe ser independiente para cada enfermedad y con datos esepcificos
            agents[agent].infection_status.update({"severity": new_severity})
            agents[agent].transition(State.INFECTED, reason=f"{self.name} worsened to {new_severity}")
            return

        # 4️⃣ Evaluar recuperación o muerte
        if days_infected >= agents[agent].incubation_period + recovery_days:
            # 🚨 CASOS CRÍTICOS: Posibilidad de muerte
            if severity == "critical" and random.random() < (mortality_risk / recovery_bonus):
                agents[agent].infection_status.update({
                    "state": State.DECEASED,
                    "contagious": False,
                    "severity": "critical"
                })
                agents[agent].transition(State.DECEASED, reason=f"{self.name} critical condition")
                return  # 🚨 agents[agent]e murió, no sigue en la simulación

            # ✅ RECUPERACIÓN: Puede ser inmune o volver a ser susceptible
            if random.random() < (self.recovery_rates.get(severity, 1.0) * recovery_bonus):
                agents[agent].infection_status.update({
                    "state": State.RECOVERED,
                    "contagious": False,
                    "severity": None,
                    "days_infected": 0,
                })
                agents[agent].transition(State.RECOVERED, reason=f"{self.name} recovery")

                # 3.3️⃣ ¿La inmunidad es temporal?
                if self.immunity_duration > 0:
                    agents[agent].infection_status["immunity_days"] = self.immunity_duration
                else:
                    agents[agent].infection_status["immunity_days"] = 0
                return

        # 5️⃣ REINFECCIÓN: Si la inmunidad es temporal, vuelve a ser susceptible
        if agents[agent].infection_status["state"] is State.RECOVERED and "immunity_days" in agents[agent].infection_status:
            agents[agent].infection_status["immunity_days"] -= 1
            if agents[agent].infection_status["immunity_days"] <= 0:
                agents[agent].infection_status.update({
                    "state": State.SUSCEPTIBLE,
                    "disease": "",
                    "severity": None,
                    "contagious": False,
                    "days_infected": 0,
                    "asymptomatic": None,
                    "immunity_days": 0
                })
                agents[agent].transition(State.SUSCEPTIBLE, reason=f"{self.name} immunity waned")
                agents[agent].immune = False  

    # def progress_infection(self, agent, agents):
    #     """
    #     Progress the infection state for the given agent.

    #     :param agent: The agent whose infection state is being progressed.
    #     """
    #     if agents[agent].infection_status["days_infected"] == 0:
    #         agents[agent].incubation_period = round(random.gauss(self.mean_incubation_period[0], self.mean_incubation_period[1]))

    #     agents[agent].infection_status["days_infected"] += 1
    #     days_infected = agents[agent].infection_status["days_infected"]

    #     # 1️⃣ INCUBACIÓN: No síntomas ni transmisión hasta que termine
    #     if days_infected <= agents[agent].incubation_period:
    #         agents[agent].infection_status["contagious"] = False
    #         return

    #     # 2️⃣ FIN DE INCUBACIÓN: Definir severidad y contagiosidad
    #     if days_infected == agents[agent].incubation_period + 1:
    #         agents[agent].infection_status["contagious"] = True  # Ya puede contagiar
    #         if agents[agent].infection_status["asymptomatic"]:
    #             agents[agent].infection_status.update({
    #                 "severity": "asymptomatic",
    #                 "state": State.INFECTED
    #             })
    #             agents[agent].transition(State.INFECTED, reason=f"{self.name} infection")
    #         else: # Si es asintomatico no se le determina la severidad
    #             severity = self.determine_severity(agents[agent])
    #             agents[agent].infection_status.update({
    #                 "severity": severity,
    #                 "state": State.INFECTED
    #             })
    #             agents[agent].transition(State.INFECTED, reason=f"{self.name} infection ({severity})")
    #         return

    #     # 3️⃣ PROGRESIÓN: Evaluar recuperación o muerte
    #     severity = agents[agent].infection_status.get("severity", "mild")
    #     recovery_days = self.severity_durations.get(severity, 10)  # Tiempo de recuperación

    #     if days_infected >= agents[agent].incubation_period + recovery_days:
    #         # 3.1️⃣ CASOS CRÍTICOS: Posibilidad de muerte
    #         if severity == "critical" and random.random() < agents[agent].update_mortality_rate(self.base_mortality_rate):
    #             agents[agent].infection_status.update({
    #                 "state": State.DECEASED,
    #                 "contagious": False,
    #                 "severity": "critical"
    #             })
    #             agents[agent].transition(State.DECEASED, reason=f"{self.name} critical condition")
    #             return  # 🚨 agents[agent]e murió, no sigue en la simulación

    #         # 3.2️⃣ RECUPERACIÓN: Puede ser inmune o volver a ser susceptible
    #         if random.random() < self.recovery_rates.get(severity, 1.0):
    #             agents[agent].infection_status.update({
    #                 "state": State.RECOVERED,
    #                 "contagious": False,
    #                 "severity": None,
    #                 "days_infected": 0,
    #             })
    #             agents[agent].transition(State.RECOVERED, reason=f"{self.name} recovery")

    #             # 3.3️⃣ ¿La inmunidad es temporal?
    #             if self.immunity_duration > 0:
    #                 agents[agent].infection_status["immunity_days"] = self.immunity_duration
    #             else:
    #                 agents[agent].infection_status["immunity_days"] = 0
    #             return

    #     # 4️⃣ REINFECCIÓN: Si la inmunidad es temporal, vuelve a ser susceptible
    #     if agents[agent].infection_status["state"] == State.RECOVERED and "immunity_days" in agents[agent].infection_status:
    #         agents[agent].infection_status["immunity_days"] -= 1
    #         if agents[agent].infection_status["immunity_days"] <= 0:
    #             agents[agent].infection_status.update({
    #                 "state": State.SUSCEPTIBLE,
    #                 "disease": "",
    #                 "severity": None,
    #                 "contagious": False,
    #                 "days_infected": 0,
    #                 "asymptomatic": None,
    #                 "immunity_days": 0
    #             })
    #             agents[agent].transition(State.SUSCEPTIBLE, reason=f"{self.name} immunity waned")
    #             agents[agent].immune = False  
  
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
