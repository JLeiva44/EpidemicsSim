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

# Example usage
if __name__ == "__main__":
    from epidemics_sim.agents.human_agent import HumanAgent

    # Example agents
    agents = [
        HumanAgent(agent_id=i, age=random.randint(0, 100), gender="male", occupation="worker", household_id=i % 10)
        for i in range(100)
    ]

    # Vaccination policy targeting elderly and essential workers
    vaccination_policy = VaccinationPolicy(vaccination_rate=0.1, effectiveness=0.8, target_groups=["elderly", "essential_workers"])

    # Apply the policy
    vaccination_policy.enforce(agents, clusters={})

    # Check results
    vaccinated_agents = [agent for agent in agents if agent.vaccinated]
    print(f"Total vaccinated agents: {len(vaccinated_agents)}")
