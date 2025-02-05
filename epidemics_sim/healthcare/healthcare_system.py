from epidemics_sim.healthcare.utils import SimulationAnalyzer
from epidemics_sim.policies.vaccination_policy import VaccinationPolicy
from epidemics_sim.policies.lockdown_policy import LockdownPolicy
from epidemics_sim.agents.base_agent import State
import random

class HealthcareSystem:
    def __init__(self, hospital_capacity, isolation_capacity, policies=[]):
        """
        Central healthcare system to monitor infections and manage responses.

        :param hospital_capacity: Number of available hospital beds.
        :param isolation_capacity: Number of available isolation spaces.
        :param policies: List of policies (e.g., lockdowns, vaccinations).
        """
        self.hospital_capacity = hospital_capacity
        self.isolation_capacity = isolation_capacity
        self.hospitalized = []
        self.isolated = []
        self.analyzer = SimulationAnalyzer()
        self.policies = policies

    def monitor_health_status(self, agents):
        """
        Monitor the health status of all agents and manage hospitalization/isolation.

        :param agents: List of agents in the simulation.
        """
        severe_cases = [a for a in agents if a.infection_status["severity"] == "severe"]
        critical_cases = [a for a in agents if a.infection_status["severity"] == "critical"]

        # Prioritize hospitalization for critical cases
        for agent in critical_cases:
            if len(self.hospitalized) < self.hospital_capacity:
                self.hospitalized.append(agent)
                agent.is_hospitalized = True
            elif len(self.isolated) < self.isolation_capacity:
                self.isolated.append(agent)
                agent.is_isolated = True

        # Hospitalize severe cases if space allows
        for agent in severe_cases:
            if len(self.hospitalized) < self.hospital_capacity:
                self.hospitalized.append(agent)
                agent.is_hospitalized = True

    def enforce_policies(self, agents, clusters):
        """
        Apply health policies based on infection rates.

        :param agents: List of agents in the simulation.
        :param clusters: Dictionary of clusters (work, home, etc.).
        """
        total_infected = sum(1 for agent in agents if agent.infection_status["state"] == State.INFECTED)

        # If more than 10% of the population is infected, enforce lockdown
        if total_infected / len(agents) > 0.1:
            lockdown = LockdownPolicy(restricted_clusters=["work", "school", "shopping"])
            lockdown.enforce(agents, clusters)

        # If vaccination policy exists, apply it
        for policy in self.policies:
            if isinstance(policy, VaccinationPolicy):
                policy.enforce(agents, clusters)

    def daily_operations(self, agents, clusters):
        """
        Perform daily health system operations.

        :param agents: List of agents in the simulation.
        :param clusters: Dictionary of clusters.
        """
        self.monitor_health_status(agents)
        self.enforce_policies(agents, clusters)
        self.analyzer.record_daily_stats(agents)
