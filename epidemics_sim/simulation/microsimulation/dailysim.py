import random
import networkx as nx
from city_cluster import CityClusterGenerator

class DailySimulation:
    def __init__(self, agents, cluster_generator, transport, config, disease_model, policies):
        """
        Initialize the daily simulation controller.

        :param agents: List of agents in the simulation.
        :param cluster_generator: Instance of CityClusterGenerator to create clusters dynamically.
        :param transport: Transport interaction handler.
        :param config: Configuration dictionary for the simulation.
        :param disease_model: Model handling the disease propagation.
        :param policies: List of active health policies.
        """
        self.agents = agents
        self.cluster_generator = cluster_generator
        self.transport = transport
        self.config = config
        self.disease_model = disease_model
        self.policies = policies
        self.clusters = self._generate_clusters()

    def _generate_clusters(self):
        """
        Generate clusters dynamically using the cluster generator.

        :return: A dictionary of generated clusters.
        """
        home_clusters = self.cluster_generator.generate_home_clusters(self.agents)
        work_clusters = self.cluster_generator.generate_work_clusters(self.agents[:len(self.agents) // 2])
        school_clusters = self.cluster_generator.generate_school_clusters(self.agents[len(self.agents) // 2:])
        shopping_clusters = self.cluster_generator.generate_shopping_clusters(self.agents)

        return {
            "home": home_clusters,
            "work": work_clusters,
            "school": school_clusters,
            "shopping": shopping_clusters
        }

    def simulate(self, days):
        """
        Simulate interactions over multiple days.

        :param days: Number of days to simulate.
        :return: Summary of interactions and disease progression over the simulation period.
        """
        simulation_results = []

        for day in range(days):
            print(f"Simulating Day {day + 1}...")
            daily_summary = self.simulate_day()
            simulation_results.append(daily_summary)

            # Update disease progression based on daily interactions
            self.disease_model.update_states()

        return simulation_results

    def simulate_day(self):
        """
        Simulate a single day of interactions.

        :return: A summary of interactions for the day.
        """
        daily_interactions = {
            "home": [],
            "work": [],
            "school": [],
            "shopping": [],
            "transport": []
        }

        # Apply health policies
        self._apply_policies()

        # Simulate home interactions
        daily_interactions["home"] = self._simulate_cluster_interactions(self.clusters["home"])

        # Simulate work interactions
        daily_interactions["work"] = self._simulate_cluster_interactions(self.clusters["work"])

        # Simulate school interactions
        daily_interactions["school"] = self._simulate_cluster_interactions(self.clusters["school"])

        # Simulate shopping interactions
        daily_interactions["shopping"] = self._simulate_cluster_interactions(self.clusters["shopping"])

        # Simulate transport interactions
        transport_interactions = self.transport.simulate_transport()
        daily_interactions["transport"].extend(transport_interactions)

        # Propagate disease based on interactions
        self.disease_model.propagate(daily_interactions)

        return daily_interactions

    def _simulate_cluster_interactions(self, cluster_list):
        """
        Simulate interactions within a list of clusters and their subclusters.

        :param cluster_list: List of clusters to simulate.
        :return: List of interactions within the clusters and subclusters.
        """
        interactions = []
        for cluster in cluster_list:
            subcluster_interactions = cluster.simulate_interactions()
            interactions.extend(subcluster_interactions)
        return interactions

    def _apply_policies(self):
        """
        Apply health policies to modify agent behavior or cluster interactions.
        """
        for policy in self.policies:
            policy.enforce(self.agents, self.clusters)

# Example configuration for the clusters and transport
example_config = {
    "home": {"duration_mean": 480, "duration_std": 120},
    "work": {"duration_mean": 480, "duration_std": 120, "min_links": 2},
    "school": {"duration_mean": 300, "duration_std": 60},
    "shopping": {"duration_mean": 37, "duration_std": 10, "max_agents": 50},
    "transport": {"interval": 5, "duration_mean": 15, "duration_std": 5},
    "household_sizes": [1, 2, 3, 4, 5, 6],
    "household_distribution": [0.1, 0.2, 0.3, 0.2, 0.15, 0.05],
    "work_sizes": [5, 10, 20, 50],
    "work_distribution": [0.4, 0.3, 0.2, 0.1],
    "school_sizes": [20, 30, 40],
    "school_distribution": [0.5, 0.3, 0.2],
    "shopping_centers": 5
}

if __name__ == "__main__":
    from population_clusters import TransportInteraction
    from epidemics_sim.diseases.disease_model import DiseaseModel
    from policies import LockdownPolicy, SocialDistancingPolicy

    # Example agents
    agents = [f"Agent_{i}" for i in range(200)]

    # Create city cluster generator
    cluster_generator = CityClusterGenerator(example_config)

    # Transport interactions
    transport_interaction = TransportInteraction(agents, example_config["transport"])

    # Disease model
    disease_model = DiseaseModel()

    # Active policies
    policies = [LockdownPolicy(), SocialDistancingPolicy()]

    # Daily simulation
    simulation = DailySimulation(agents, cluster_generator, transport_interaction, example_config, disease_model, policies)
    simulation_results = simulation.simulate(days=10)
    print("Simulation Results Summary:", simulation_results)
