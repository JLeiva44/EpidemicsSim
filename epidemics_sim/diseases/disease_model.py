import random
from abc import ABC, abstractmethod

class DiseaseModel(ABC):
    def __init__(self, transmission_rate, recovery_rate, mortality_rate):
        """
        Base class for diseases transmitted by contact.

        :param transmission_rate: Probability of transmission per contact.
        :param recovery_rate: Probability of recovery per day.
        :param mortality_rate: Probability of death if in critical condition.
        """
        self.transmission_rate = transmission_rate
        self.recovery_rate = recovery_rate
        self.mortality_rate = mortality_rate

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
        if target.infection_status["state"] == "susceptible" and not target.immune:
            transmission_probability = self.calculate_transmission_probability(source, target)
            if random.random() < transmission_probability:
                target.infection_status["state"] = "infected"

    @abstractmethod
    def calculate_transmission_probability(self, source, target):
        """
        Calculate the transmission probability specific to the disease.

        :param source: Source agent.
        :param target: Target agent.
        :return: Transmission probability.
        """
        pass

    def update_states(self, agents):
        """
        Update the state of all agents, progressing infections.

        :param agents: List of agents in the simulation.
        """
        for agent in agents:
            if agent.infection_status["state"] == "infected":
                self._progress_infection(agent)

    def _progress_infection(self, agent):
        """
        Progress the infection state of an agent, including recovery and mortality.

        :param agent: The agent to update.
        """
        agent.days_infected += 1

        # Check for recovery
        if random.random() < self.recovery_rate:
            agent.infection_status["state"] = "recovered"
            agent.immune = True
            return

        # Check for mortality
        if agent.infection_status.get("severity", "mild") == "critical":
            if random.random() < self.mortality_rate:
                agent.infection_status["state"] = "deceased"

    @abstractmethod
    def determine_severity(self, agent):
        """
        Determine the severity of the disease for an infected agent.

        :param agent: The agent whose severity is being determined.
        :return: Severity level ('mild', 'moderate', 'severe', 'critical').
        """
        pass