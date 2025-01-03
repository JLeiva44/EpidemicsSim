import random
import networkx as nx

class DailySimulation:
    def __init__(self, agents, clusters, transport, config, disease_model, policies):
        """
        Initialize the daily simulation controller.

        :param agents: List of agents in the simulation.
        :param clusters: Dictionary of clusters (home, work, school, shopping).
        :param transport: Transport interaction handler.
        :param config: Configuration dictionary for the simulation.
        :param disease_model: Model handling the disease propagation.
        :param policies: List of active health policies.
        """
        self.agents = agents
        self.clusters = clusters
        self.transport = transport
        self.config = config
        self.disease_model = disease_model
        self.policies = policies

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
        Simulate interactions within a list of clusters.

        :param cluster_list: List of clusters to simulate.
        :return: List of interactions within the clusters.
        """
        interactions = []
        for cluster in cluster_list:
            graph = cluster.generate_graph()
            duration = cluster.get_contact_duration()
            interactions.append((graph, duration))
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
}

# Example usage
if __name__ == "__main__":
    from clusters import HomeCluster, WorkCluster, SchoolCluster, ShoppingCluster
    from transport import TransportInteraction
    from disease import DiseaseModel
    from policies import LockdownPolicy, SocialDistancingPolicy

    # Example agents
    agents = [f"Agent_{i}" for i in range(100)]

    # Create clusters
    home_clusters = [HomeCluster(agents[i:i + 5], example_config["home"]) for i in range(0, 20, 5)]
    work_clusters = [WorkCluster(agents[i:i + 10], example_config["work"]) for i in range(20, 50, 10)]
    school_clusters = [SchoolCluster(agents[i:i + 10], example_config["school"]) for i in range(50, 80, 10)]
    shopping_clusters = [ShoppingCluster(agents[i:i + 10], example_config["shopping"]) for i in range(80, 100, 10)]

    clusters = {
        "home": home_clusters,
        "work": work_clusters,
        "school": school_clusters,
        "shopping": shopping_clusters
    }

    # Transport interactions
    transport_interaction = TransportInteraction(agents, example_config["transport"])

    # Disease model
    disease_model = DiseaseModel()

    # Active policies
    policies = [LockdownPolicy(), SocialDistancingPolicy()]

    # Daily simulation
    simulation = DailySimulation(agents, clusters, transport_interaction, example_config, disease_model, policies)
    simulation_results = simulation.simulate(days=10)
    print("Simulation Results Summary:", simulation_results)
