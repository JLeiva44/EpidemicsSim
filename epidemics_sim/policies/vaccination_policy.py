from .base_policy import Policy
import random
class VaccinationPolicy(Policy):
    def __init__(self, vaccination_rate):
        """
        Initialize the vaccination policy.

        :param vaccination_rate: Proportion of agents to vaccinate.
        """
        self.vaccination_rate = vaccination_rate

    def enforce(self, agents, clusters):
        """
        Vaccinate a proportion of agents.

        :param agents: List of agents in the simulation.
        :param clusters: Dictionary of clusters in the simulation.
        """
        num_to_vaccinate = int(len(agents) * self.vaccination_rate)
        susceptible_agents = [agent for agent in agents if agent.state == "susceptible"]
        vaccinated_agents = random.sample(susceptible_agents, min(num_to_vaccinate, len(susceptible_agents)))

        for agent in vaccinated_agents:
            agent.state = "immune"