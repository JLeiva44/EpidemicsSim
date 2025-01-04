import random
from clusters_whit_subclusters import ClusterWithSubclusters

class CityClusterGenerator:
    def __init__(self, config):
        """
        Initialize the city cluster generator.

        :param config: Configuration dictionary containing parameters for generating clusters.
        """
        self.config = config

    def generate_home_clusters(self, agents):
        """
        Generate home clusters based on city-specific data.

        :param agents: List of agents to assign to home clusters.
        :return: List of home clusters.
        """
        household_sizes = self.config.get("household_sizes", [1, 2, 3, 4, 5, 6])
        household_distribution = self.config.get("household_distribution", [0.1, 0.2, 0.3, 0.2, 0.15, 0.05])
        clusters = []
        unassigned_agents = agents.copy()

        while unassigned_agents:
            size = random.choices(household_sizes, household_distribution)[0]
            size = min(size, len(unassigned_agents))
            cluster_agents = unassigned_agents[:size]
            unassigned_agents = unassigned_agents[size:]
            clusters.append(ClusterWithSubclusters(cluster_agents, self.config, "home", "home"))

        return clusters

    def generate_work_clusters(self, agents):
        """
        Generate work clusters with subclusters (e.g., companies) based on city-specific data.

        :param agents: List of agents to assign to work clusters.
        :return: List of work clusters with subclusters.
        """
        return self._generate_clusters_with_subclusters(agents, "work", "work")

    def generate_school_clusters(self, agents):
        """
        Generate school clusters with subclusters (e.g., schools) based on city-specific data.

        :param agents: List of agents to assign to school clusters.
        :return: List of school clusters with subclusters.
        """
        return self._generate_clusters_with_subclusters(agents, "school", "school")

    def generate_shopping_clusters(self, agents):
        """
        Generate shopping clusters with subclusters (e.g., shopping centers).

        :param agents: List of agents to assign to shopping clusters.
        :return: List of shopping clusters with subclusters.
        """
        return self._generate_clusters_with_subclusters(agents, "shopping", "shopping")

    def _generate_clusters_with_subclusters(self, agents, cluster_type, config_key):
        """
        Generalized method to generate clusters with subclusters.

        :param agents: List of agents to assign to the cluster.
        :param cluster_type: Type of cluster (e.g., "work", "school").
        :param config_key: Configuration key for subcluster parameters.
        :return: List of clusters with subclusters.
        """
        subcluster_config = self.config.get(config_key, {})
        subclusters = []
        unassigned_agents = agents.copy()

        while unassigned_agents:
            size = random.choices(
                subcluster_config.get("size_ranges", []),
                subcluster_config.get("distribution", [])
            )[0]
            size = min(size, len(unassigned_agents))
            cluster_agents = unassigned_agents[:size]
            unassigned_agents = unassigned_agents[size:]

            subclusters.append(ClusterWithSubclusters(cluster_agents, self.config, cluster_type, config_key))

        return subclusters

# Example Configuration
example_config = {
    "household_sizes": [1, 2, 3, 4, 5, 6],
    "household_distribution": [0.1, 0.2, 0.3, 0.2, 0.15, 0.05],
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
    },
    "shopping": {
        "size_ranges": [10, 20, 30],
        "distribution": [0.5, 0.3, 0.2],
        "duration_mean": 37,
        "duration_std": 10
    }
}

# Example Usage
if __name__ == "__main__":
    from cluster_with_subclusters import Subcluster

    # Example agents
    agents = [f"Agent_{i}" for i in range(200)]

    generator = CityClusterGenerator(example_config)

    # Generate clusters
    home_clusters = generator.generate_home_clusters(agents[:100])
    work_clusters = generator.generate_work_clusters(agents[:100])
    school_clusters = generator.generate_school_clusters(agents[100:150])
    shopping_clusters = generator.generate_shopping_clusters(agents)

    print(f"Generated {len(home_clusters)} home clusters.")
    print(f"Generated {len(work_clusters)} work clusters.")
    print(f"Generated {len(school_clusters)} school clusters.")
    print(f"Generated {len(shopping_clusters)} shopping clusters.")
