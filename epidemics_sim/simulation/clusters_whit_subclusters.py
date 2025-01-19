import random
import networkx as nx

class Subcluster:
    def __init__(self, agents, config, active_periods):
        """
        Initialize a subcluster.

        :param agents: List of agents assigned to the subcluster.
        :param config: Configuration dictionary for the subcluster.
        :param active_periods: List of periods during which the subcluster is active (e.g., ["morning", "daytime"]).
        """
        self.agents = agents
        self.config = config
        self.active_periods = active_periods

    def generate_graph(self):
        """
        Generate a complete graph for the subcluster.

        :return: A NetworkX graph representing the subcluster.
        """
        graph = nx.complete_graph(len(self.agents))
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
        unassigned_agents = self.agents.copy()

        while unassigned_agents:
            size = random.choices(subcluster_sizes, subcluster_distribution)[0]
            size = min(size, len(unassigned_agents))
            subcluster_agents = unassigned_agents[:size]
            unassigned_agents = unassigned_agents[size:]

            subcluster_config = self.config[subcluster_config_key]
            subcluster = Subcluster(subcluster_agents, subcluster_config, active_periods)
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
    },
    "school": {
        "size_ranges": [20, 30, 40],
        "distribution": [0.5, 0.3, 0.2],
        "active_periods": ["morning", "daytime"],
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
