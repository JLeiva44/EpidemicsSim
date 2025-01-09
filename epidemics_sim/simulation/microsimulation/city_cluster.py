import random
from clusters_whit_subclusters import ClusterWithSubclusters

class CityClusterGenerator:
    def __init__(self, config, municipal_data):
        """
        Initialize the city cluster generator.

        :param config: Configuration dictionary containing parameters for generating clusters.
        :param municipal_data: Dictionary with municipal-specific data (e.g., population distribution, cluster sizes).
        """
        self.config = config
        self.municipal_data = municipal_data

    def _get_agents_by_municipio(self, agents, municipio):
        """
        Filter agents belonging to a specific municipio.

        :param agents: List of agents.
        :param municipio: Name of the municipio.
        :return: List of agents belonging to the municipio.
        """
        return [agent for agent in agents if agent.municipio == municipio]

    def generate_home_clusters(self, agents):
        """
        Generate home clusters based on municipal-specific data.

        :param agents: List of agents to assign to home clusters.
        :return: List of home clusters.
        """
        clusters = []

        for municipio, data in self.municipal_data.items():
            municipio_agents = self._get_agents_by_municipio(agents, municipio)
            household_sizes = data.get("household_sizes", [1, 2, 3, 4, 5, 6])
            household_distribution = data.get("household_distribution", [0.1, 0.2, 0.3, 0.2, 0.15, 0.05])

            unassigned_agents = municipio_agents.copy()
            while unassigned_agents:
                size = random.choices(household_sizes, household_distribution)[0]
                size = min(size, len(unassigned_agents))
                cluster_agents = unassigned_agents[:size]
                unassigned_agents = unassigned_agents[size:]
                clusters.append(ClusterWithSubclusters(cluster_agents, self.config, "home", "home"))

        return clusters

    def generate_work_clusters(self, agents):
        """
        Generate work clusters with subclusters (e.g., companies) based on municipal-specific data and inter-municipal probabilities.

        :param agents: List of agents to assign to work clusters.
        :return: List of work clusters with subclusters.
        """
        clusters = []

        for municipio, data in self.municipal_data.items():
            municipio_agents = self._get_agents_by_municipio(agents, municipio)
            inter_municipal_prob = data.get("inter_municipal_work_prob", {})

            # Assign agents to work clusters considering inter-municipal probabilities
            for target_municipio, prob in inter_municipal_prob.items():
                target_agents = [
                    agent for agent in municipio_agents if random.random() < prob
                ]
                municipio_agents = [agent for agent in municipio_agents if agent not in target_agents]

                clusters.extend(self._generate_clusters_with_subclusters(target_agents, "work", "work"))

            # Assign remaining agents to work clusters within the same municipio
            clusters.extend(self._generate_clusters_with_subclusters(municipio_agents, "work", "work"))

        return clusters

    def generate_school_clusters(self, agents):
        """
        Generate school clusters with subclusters (e.g., schools) based on municipal-specific data.

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
        Generalized method to generate clusters with subclusters based on municipal data.

        :param agents: List of agents to assign to the cluster.
        :param cluster_type: Type of cluster (e.g., "work", "school").
        :param config_key: Configuration key for subcluster parameters.
        :return: List of clusters with subclusters.
        """
        clusters = []

        for municipio, data in self.municipal_data.items():
            municipio_agents = self._get_agents_by_municipio(agents, municipio)
            subcluster_sizes = data.get(f"{config_key}_sizes", [5, 10, 20])
            subcluster_distribution = data.get(f"{config_key}_distribution", [0.4, 0.3, 0.3])

            unassigned_agents = municipio_agents.copy()
            while unassigned_agents:
                size = random.choices(subcluster_sizes, subcluster_distribution)[0]
                size = min(size, len(unassigned_agents))
                cluster_agents = unassigned_agents[:size]
                unassigned_agents = unassigned_agents[size:]

                clusters.append(ClusterWithSubclusters(cluster_agents, self.config, cluster_type, config_key))

        return clusters

# Example Configuration
example_config = {
    "home": {
        "duration_mean": 480,
        "duration_std": 120
    },
    "work": {
        "duration_mean": 480,
        "duration_std": 120
    },
    "school": {
        "duration_mean": 300,
        "duration_std": 60
    },
    "shopping": {
        "duration_mean": 37,
        "duration_std": 10
    }
}

example_municipal_data = {
    "Municipio_1": {
        "household_sizes": [1, 2, 3, 4],
        "household_distribution": [0.2, 0.3, 0.3, 0.2],
        "work_sizes": [5, 10, 15],
        "work_distribution": [0.5, 0.3, 0.2],
        "school_sizes": [20, 30, 40],
        "school_distribution": [0.4, 0.4, 0.2],
        "inter_municipal_work_prob": {"Municipio_2": 0.3, "Municipio_3": 0.1}
    },
    "Municipio_2": {
        "household_sizes": [2, 3, 4, 5],
        "household_distribution": [0.1, 0.3, 0.4, 0.2],
        "work_sizes": [10, 20, 50],
        "work_distribution": [0.4, 0.4, 0.2],
        "school_sizes": [25, 35, 45],
        "school_distribution": [0.3, 0.5, 0.2],
        "inter_municipal_work_prob": {"Municipio_1": 0.2, "Municipio_3": 0.15}
    }
}

# Example Usage
if __name__ == "__main__":
    from clusters_whit_subclusters import Subcluster

    # Example agents
    agents = [f"Agent_{i}" for i in range(200)]

    generator = CityClusterGenerator(example_config, example_municipal_data)

    # Generate clusters
    home_clusters = generator.generate_home_clusters(agents[:100])
    work_clusters = generator.generate_work_clusters(agents[:100])
    school_clusters = generator.generate_school_clusters(agents[100:150])
    shopping_clusters = generator.generate_shopping_clusters(agents)

    print(f"Generated {len(home_clusters)} home clusters.")
    print(f"Generated {len(work_clusters)} work clusters.")
    print(f"Generated {len(school_clusters)} school clusters.")
    print(f"Generated {len(shopping_clusters)} shopping clusters.")
