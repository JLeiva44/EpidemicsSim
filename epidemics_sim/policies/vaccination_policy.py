from epidemics_sim.policies.base_policy import Policy
import random

class VaccinationPolicy(Policy):
    def __init__(self, vaccination_rate, effectiveness, target_groups=None):
        """
        Initialize the vaccination policy.

        :param vaccination_rate: Daily percentage of the population to vaccinate.
        :param effectiveness: Vaccine effectiveness (reduction in infection probability).
        :param target_groups: Optional list of target groups (e.g., 'elderly', 'healthcare workers').
        """
        self.vaccination_rate = vaccination_rate
        self.effectiveness = effectiveness
        self.target_groups = target_groups or []

    def enforce(self, agents, clusters):
        """
        Apply vaccination to the population based on the policy parameters.

        :param agents: List of agents in the simulation.
        :param clusters: Dictionary of clusters in the simulation.
        """
        eligible_agents = [agent for agent in agents if not agent.vaccinated]

        # Filter by target groups if specified
        if self.target_groups:
            eligible_agents = self._filter_by_target_groups(eligible_agents)

        # Determine the number of agents to vaccinate
        num_to_vaccinate = int(len(agents) * self.vaccination_rate)
        agents_to_vaccinate = random.sample(eligible_agents, min(num_to_vaccinate, len(eligible_agents)))

        for agent in agents_to_vaccinate:
            self._vaccinate_agent(agent)

    def _filter_by_target_groups(self, agents):
        """
        Filter agents based on the specified target groups.

        :param agents: List of agents to filter.
        :return: Filtered list of agents.
        """
        filtered_agents = []
        for agent in agents:
            if "elderly" in self.target_groups and agent.age > 60:
                filtered_agents.append(agent)
            if "healthcare_workers" in self.target_groups and agent.occupation == "healthcare_worker":
                filtered_agents.append(agent)
            if "essential_workers" in self.target_groups and agent.occupation in ["worker", "teacher"]:
                filtered_agents.append(agent)
        return filtered_agents

    def _vaccinate_agent(self, agent):
        """
        Vaccinate an agent, modifying their attributes.

        :param agent: The agent to vaccinate.
        """
        agent.vaccinated = True
        agent.vaccine_effectiveness = self.effectiveness

