import random
from epidemics_sim.agents.base_agent import State

class StateManager:
    def __init__(self, severity_func, recovery_func, mortality_rate):
        """
        Initialize the state manager.

        :param severity_func: Function to determine the severity of the infection.
        :param recovery_func: Function to evaluate recovery or mortality.
        :param mortality_rate: Base probability of mortality for critical cases.
        """
        self.severity_func = severity_func
        self.recovery_func = recovery_func
        self.mortality_rate = mortality_rate

    def evaluate_state(self, agent):
        """
        Evaluate and update the state of an agent based on their current condition.

        :param agent: The agent whose state is being evaluated.
        """
        if agent.state == State.INFECTED:
            self._progress_infection(agent)

    