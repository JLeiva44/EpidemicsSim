import random
import networkx as nx

class Subcluster:
    def __init__(self, agents, config, active_periods, interaction_density=1.0):
        """
        Initialize a subcluster.

        :param agents: List of agents assigned to the subcluster.
        :param config: Configuration dictionary for the subcluster.
        :param active_periods: List of periods during which the subcluster is active.
        :param interaction_density: Proportion of possible interactions (default 1.0 for full graph).
        """
        self.agents = agents
        self.config = config
        self.active_periods = active_periods
        self.interaction_density = interaction_density

    def generate_graph(self):
        """
        Generate a graph for the subcluster.

        :return: A NetworkX graph representing the subcluster.
        """
        num_agents = len(self.agents)
        if self.interaction_density == 1.0:
            graph = nx.complete_graph(num_agents)
        else:
            graph = nx.erdos_renyi_graph(num_agents, self.interaction_density)

        for i, agent in enumerate(self.agents):
            graph.nodes[i]["agent"] = agent
        return graph

    def simulate_interactions(self, time_period):
        """
        Simulate interactions for the subcluster during a specific time period.

        :param time_period: The time period (e.g., "morning", "daytime", "evening", "night").
        :return: List of interactions within the subcluster.
        """
        if time_period not in self.active_periods:
            return []

        graph = self.generate_graph()
        interactions = []

        for edge in graph.edges:
            agent1 = graph.nodes[edge[0]]["agent"]
            agent2 = graph.nodes[edge[1]]["agent"]
            interactions.append((agent1, agent2))

        return interactions


class ClusterWithSubclusters:
    def __init__(self, agents, config, subcluster_type, subcluster_config_key):
        """
        Initialize a cluster with subclusters.

        :param agents: List of agents assigned to the cluster.
        :param config: Configuration dictionary for the cluster.
        :param subcluster_type: Type of subcluster (e.g., "company", "school").
        :param subcluster_config_key: Key in the configuration for subcluster parameters.
        """
        self.agents = agents
        self.subclusters = []
        self.config = config
        self.subcluster_type = subcluster_type

        self._generate_subclusters(subcluster_config_key)

    def _generate_subclusters(self, subcluster_config_key):
        """
        Generate subclusters for this cluster based on configuration.

        :param subcluster_config_key: Key in the configuration for subcluster parameters.
        """
        subcluster_sizes = self.config[subcluster_config_key].get("size_ranges", [])
        subcluster_distribution = self.config[subcluster_config_key].get("distribution", [])
        active_periods = self.config[subcluster_config_key].get("active_periods", [])
        interaction_density = self.config[subcluster_config_key].get("interaction_density", 1.0)
        unassigned_agents = self.agents.copy()

        while unassigned_agents:
            size = random.choices(subcluster_sizes, subcluster_distribution)[0]
            size = min(size, len(unassigned_agents))
            subcluster_agents = unassigned_agents[:size]
            unassigned_agents = unassigned_agents[size:]

            subcluster_config = self.config[subcluster_config_key]
            subcluster = Subcluster(subcluster_agents, subcluster_config, active_periods, interaction_density)
            self.subclusters.append(subcluster)

    def simulate_interactions(self, time_period):
        """
        Simulate interactions for all subclusters within this cluster during a specific time period.

        :param time_period: The time period (e.g., "morning", "daytime", "evening", "night").
        :return: List of interactions within all subclusters.
        """
        interactions = []
        for subcluster in self.subclusters:
            subcluster_interactions = subcluster.simulate_interactions(time_period)
            interactions.extend(subcluster_interactions)
        return interactions

# Example Configuration
example_config = {
    "work": {
        "size_ranges": [5, 10, 20, 50],
        "distribution": [0.4, 0.3, 0.2, 0.1],
        "active_periods": ["daytime"],
        "interaction_density": 0.8,
    },
    "school": {
        "size_ranges": [20, 30, 40],
        "distribution": [0.5, 0.3, 0.2],
        "active_periods": ["morning", "daytime"],
        "interaction_density": 0.9,
    },
}

# Example Usage
if __name__ == "__main__":
    # Example agents
    agents = [f"Agent_{i}" for i in range(100)]

    # Work cluster with subclusters (companies)
    work_cluster = ClusterWithSubclusters(
        agents[:50],
        example_config,
        subcluster_type="company",
        subcluster_config_key="work",
    )
    work_interactions = work_cluster.simulate_interactions("daytime")
    print(f"Work Interactions: {len(work_interactions)} edges simulated.")

    # School cluster with subclusters (schools)
    school_cluster = ClusterWithSubclusters(
        agents[50:],
        example_config,
        subcluster_type="school",
        subcluster_config_key="school",
    )
    school_interactions = school_cluster.simulate_interactions("morning")
    print(f"School Interactions: {len(school_interactions)} edges simulated.")
