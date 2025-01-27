import random
from abc import ABC, abstractmethod
from epidemics_sim.agents.base_agent import State

class DiseaseModel(ABC):
    def __init__(self, name, transmission_rate, incubation_period, asymptomatic_probability, base_mortality_rate):
        """
        Base class for diseases transmitted by contact.

        :param name: Name of the disease (e.g., "COVID-19").
        :param transmission_rate: Probability of transmission per contact.
        :param incubation_period: Number of days before symptoms or contagion begins.
        :param asymptomatic_probability: Probability of an agent being asymptomatic.
        :param base_mortality_rate: Base mortality rate for critical cases.
        """
        self.name = name
        self.transmission_rate = transmission_rate
        self.incubation_period = incubation_period
        self.asymptomatic_probability = asymptomatic_probability
        self.base_mortality_rate = base_mortality_rate

    def propagate(self, daily_interactions):
        """
        Handle the propagation of the disease based on daily interactions.

        :param daily_interactions: Dictionary of daily interactions by time intervals.
        """
        for time_period, interactions in daily_interactions.items():
            for interaction in interactions:  # Each interaction is a tuple (agent1, agent2)
                self._evaluate_transmission(interaction)

    def _evaluate_transmission(self, interaction):
        """
        Evaluate transmission between two agents.

        :param interaction: Tuple (agent1, agent2).
        """
        agent1, agent2 = interaction
        self._attempt_infection(agent1, agent2)
        self._attempt_infection(agent2, agent1)

    def _attempt_infection(self, source, target):
        """
        Attempt to infect the target agent from the source agent.

        :param source: Source agent.
        :param target: Target agent.
        """
        if target.state == State.SUSCEPTIBLE and not target.immune:
            transmission_probability = self.calculate_transmission_probability(source, target)
            if random.random() < transmission_probability:
                target.transition(State.INFECTED, reason=f"Infected by {self.name}")
                target.infection_status.update({
                    "disease": self.name,
                    "contagious": False,
                    "severity": None,
                    "days_infected": 0
                })

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
            probability *= 0.5

        # Adjust for mask usage
        if source.mask_usage or target.mask_usage:
            probability *= 0.7

        return probability

    def progress_infection(self, agent):
        """
        Handle the progression of the infection for the given agent.

        :param agent: The agent whose infection state is being progressed.
        """
        agent.infection_status["days_infected"] += 1
        days_infected = agent.infection_status["days_infected"]

        # Handle incubation period
        if days_infected <= self.incubation_period:
            agent.infection_status["contagious"] = False
            return

        # End of incubation: determine symptoms or asymptomatic status
        if days_infected == self.incubation_period + 1:
            agent.infection_status["contagious"] = True
            if random.random() < self.asymptomatic_probability:
                agent.infection_status["severity"] = "asymptomatic"
                agent.transition(State.ASYMPTOMATIC, reason=f"{self.name} infection")
            else:
                severity = self.determine_severity(agent)
                agent.infection_status["severity"] = severity
                agent.transition(State.SYMPTOMATIC, reason=f"{self.name} infection ({severity})")

        # Handle recovery or death
        if days_infected >= self.incubation_period + 10:
            if agent.infection_status["severity"] == "critical":
                if random.random() < self.base_mortality_rate:
                    agent.transition(State.DECEASED, reason=f"{self.name} critical condition")
                    return
            agent.transition(State.RECOVERED, reason=f"{self.name} recovery")
            agent.immune = True

    @abstractmethod
    def determine_severity(self, agent):
        """
        Determine the severity of the disease for an agent.

        :param agent: The agent whose severity is being determined.
        :return: Severity level ('mild', 'moderate', 'severe', 'critical').
        """
        pass
