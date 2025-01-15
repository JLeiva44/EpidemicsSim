import random
import networkx as nx

class Subcluster:
    def __init__(self, agents, config):
        """
        Initialize a subcluster.

        :param agents: List of agents assigned to the subcluster.
        :param config: Configuration dictionary for the subcluster.
        """
        self.agents = agents
        self.duration_mean = config.get("duration_mean", 300)
        self.duration_std = config.get("duration_std", 60)

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
        if not self._is_active_during(time_period):
            return []

        graph = self.generate_graph()
        duration = self.get_contact_duration()
        interactions = []

        for edge in graph.edges:
            agent1 = graph.nodes[edge[0]]["agent"]
            agent2 = graph.nodes[edge[1]]["agent"]
            interactions.append((agent1, agent2, duration))

        return interactions

    def get_contact_duration(self):
        """
        Get the contact duration for this subcluster.

        :return: Randomized contact duration based on configuration.
        """
        return max(0, random.gauss(self.duration_mean, self.duration_std))

    def _is_active_during(self, time_period):
        """
        Determine if the subcluster is active during a given time period.

        :param time_period: The time period to check.
        :return: Boolean indicating whether the subcluster is active.
        """
        active_periods = ["morning", "daytime", "evening"]  # Example: Define active periods
        return time_period in active_periods


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
        unassigned_agents = self.agents.copy()

        while unassigned_agents:
            size = random.choices(subcluster_sizes, subcluster_distribution)[0]
            size = min(size, len(unassigned_agents))
            subcluster_agents = unassigned_agents[:size]
            unassigned_agents = unassigned_agents[size:]

            subcluster_config = self.config[subcluster_config_key]
            subcluster = Subcluster(subcluster_agents, subcluster_config)
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
        "duration_mean": 480,
        "duration_std": 120
    },
    "school": {
        "size_ranges": [20, 30, 40],
        "distribution": [0.5, 0.3, 0.2],
        "duration_mean": 300,
        "duration_std": 60
    }
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
        subcluster_config_key="work"
    )
    work_interactions = work_cluster.simulate_interactions("daytime")
    print(f"Work Interactions: {len(work_interactions)} subclusters simulated.")

    # School cluster with subclusters (schools)
    school_cluster = ClusterWithSubclusters(
        agents[50:],
        example_config,
        subcluster_type="school",
        subcluster_config_key="school"
    )
    school_interactions = school_cluster.simulate_interactions("morning")
    print(f"School Interactions: {len(school_interactions)} subclusters simulated.")



# import random
# import networkx as nx

# class Subcluster:
#     def __init__(self, agents, config):
#         """
#         Initialize a subcluster.

#         :param agents: List of agents assigned to the subcluster.
#         :param config: Configuration dictionary for the subcluster.
#         """
#         self.agents = agents
#         self.duration_mean = config.get("duration_mean", 300)
#         self.duration_std = config.get("duration_std", 60)

#     def generate_graph(self):
#         """
#         Generate a complete graph for the subcluster.

#         :return: A NetworkX graph representing the subcluster.
#         """
#         graph = nx.complete_graph(len(self.agents))
#         for i, agent in enumerate(self.agents):
#             graph.nodes[i]["agent"] = agent
#         return graph

#     def get_contact_duration(self):
#         """
#         Get the contact duration for this subcluster.

#         :return: Randomized contact duration based on configuration.
#         """
#         return max(0, random.gauss(self.duration_mean, self.duration_std))


# class ClusterWithSubclusters:
#     def __init__(self, agents, config, subcluster_type, subcluster_config_key):
#         """
#         Initialize a cluster with subclusters.

#         :param agents: List of agents assigned to the cluster.
#         :param config: Configuration dictionary for the cluster.
#         :param subcluster_type: Type of subcluster (e.g., "company", "school").
#         :param subcluster_config_key: Key in the configuration for subcluster parameters.
#         """
#         self.agents = agents
#         self.subclusters = []
#         self.config = config
#         self.subcluster_type = subcluster_type

#         self._generate_subclusters(subcluster_config_key)

#     def _generate_subclusters(self, subcluster_config_key):
#         """
#         Generate subclusters for this cluster based on configuration.

#         :param subcluster_config_key: Key in the configuration for subcluster parameters.
#         """
#         subcluster_sizes = self.config[subcluster_config_key].get("size_ranges", [])
#         subcluster_distribution = self.config[subcluster_config_key].get("distribution", [])
#         unassigned_agents = self.agents.copy()

#         while unassigned_agents:
#             size = random.choices(subcluster_sizes, subcluster_distribution)[0]
#             size = min(size, len(unassigned_agents))
#             subcluster_agents = unassigned_agents[:size]
#             unassigned_agents = unassigned_agents[size:]

#             subcluster_config = self.config[subcluster_config_key]
#             subcluster = Subcluster(subcluster_agents, subcluster_config)
#             self.subclusters.append(subcluster)

#     def simulate_interactions(self):
#         """
#         Simulate interactions for all subclusters within this cluster.

#         :return: List of interactions within all subclusters.
#         """
#         interactions = []
#         for subcluster in self.subclusters:
#             graph = subcluster.generate_graph()
#             duration = subcluster.get_contact_duration()
#             interactions.append((graph, duration))
#         return interactions

# # Example Configuration
# example_config = {
#     "work": {
#         "size_ranges": [5, 10, 20, 50],
#         "distribution": [0.4, 0.3, 0.2, 0.1],
#         "duration_mean": 480,
#         "duration_std": 120
#     },
#     "school": {
#         "size_ranges": [20, 30, 40],
#         "distribution": [0.5, 0.3, 0.2],
#         "duration_mean": 300,
#         "duration_std": 60
#     }
# }

# # Example Usage
# if __name__ == "__main__":
#     # Example agents
#     agents = [f"Agent_{i}" for i in range(100)]

#     # Work cluster with subclusters (companies)
#     work_cluster = ClusterWithSubclusters(
#         agents[:50],
#         example_config,
#         subcluster_type="company",
#         subcluster_config_key="work"
#     )
#     work_interactions = work_cluster.simulate_interactions()
#     print(f"Work Interactions: {len(work_interactions)} subclusters simulated.")

#     # School cluster with subclusters (schools)
#     school_cluster = ClusterWithSubclusters(
#         agents[50:],
#         example_config,
#         subcluster_type="school",
#         subcluster_config_key="school"
#     )
#     school_interactions = school_cluster.simulate_interactions()
#     print(f"School Interactions: {len(school_interactions)} subclusters simulated.")
