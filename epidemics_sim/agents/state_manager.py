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

    def _progress_infection(self, agent):
        """
        Progress the infection state for an agent.

        :param agent: The infected agent.
        """
        agent.days_infected += 1

        # Incubation period: no symptoms or contagion during initial days
        if agent.days_infected <= agent.incubation_period:
            return

        # Determine severity once incubation ends
        if agent.days_infected == agent.incubation_period + 1 and not agent.infection_status["severity"]:
            agent.infection_status["severity"] = self.severity_func(agent)

        # Evaluate recovery or mortality after 10 days of symptoms
        if agent.days_infected >= agent.incubation_period + 10:
            if agent.infection_status["severity"] in ["critical", State.CRITICAL]:
                # Critical cases have a chance of mortality
                if random.random() < self.mortality_rate:
                    agent.transition(State.DECEASED, reason="Critical condition")
                    return

            # Evaluate recovery
            new_state = self.recovery_func(agent)
            agent.transition(new_state, reason="Infection progression")

    def reset_agent(self, agent):
        """
        Reset the agent to a susceptible state after recovery.

        :param agent: The recovered agent.
        """
        agent.reset_infection()

    def enforce_isolation(self, agent, days):
        """
        Enforce isolation rules on an agent, preventing state progression.

        :param agent: The agent to isolate.
        :param days: Number of days the agent will be isolated.
        """
        agent.isolated = True
        agent.isolation_days = days

    def manage_vaccination(self, agent, efficacy):
        """
        Manage vaccination effects on an agent.

        :param agent: The agent being vaccinated.
        :param efficacy: Efficacy of the vaccine in reducing transmission/severity.
        """
        if random.random() < efficacy:
            agent.immune = True
            agent.transition(State.RECOVERED_IMMUNE, reason="Vaccination")

    def release_isolation(self, agent):
        """
        Release an agent from isolation once the period ends.

        :param agent: The agent to release.
        """
        if agent.isolated:
            agent.isolation_days -= 1
            if agent.isolation_days <= 0:
                agent.isolated = False
                agent.isolation_days = 0

# Example functions for severity and recovery
def determine_severity(agent):
    """
    Determine the severity of the disease for an agent.
    Adjusts based on age, comorbidities, etc.
    """
    probabilities = [0.6, 0.25, 0.1, 0.05]
    if agent.age > 60 or "comorbidities" in agent.attributes:
        probabilities = [0.5, 0.3, 0.15, 0.05]  # Adjusted probabilities
    return random.choices(["mild", "moderate", "severe", "critical"], probabilities)[0]

def evaluate_recovery(agent):
    """
    Evaluate recovery or mortality for an agent.
    Returns the new state.
    """
    if agent.infection_status["severity"] in ["mild", "moderate"]:
        return State.RECOVERED
    if agent.infection_status["severity"] == "severe" and random.random() < 0.8:
        return State.RECOVERED
    return State.CRITICAL  # Default for severe cases without recovery
