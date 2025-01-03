import random
import networkx as nx

class HomeCluster:
    def __init__(self, agents, config):
        """
        Initialize a home cluster.

        :param agents: List of agents assigned to the home.
        :param config: Configuration dictionary for the home cluster.
        """
        self.agents = agents
        self.duration_mean = config.get("duration_mean", 480)  # Default 8 hours
        self.duration_std = config.get("duration_std", 120)    # Default 2 hours

    def generate_graph(self):
        """
        Generate a complete graph for the home cluster.

        :return: A NetworkX graph representing the home.
        """
        graph = nx.complete_graph(len(self.agents))
        for i, agent in enumerate(self.agents):
            graph.nodes[i]["agent"] = agent
        return graph

    def get_contact_duration(self):
        """
        Get the contact duration for this cluster.

        :return: Randomized contact duration based on configuration.
        """
        return max(0, random.gauss(self.duration_mean, self.duration_std))


class WorkCluster:
    def __init__(self, agents, config):
        """
        Initialize a work cluster.

        :param agents: List of agents assigned to the workplace.
        :param config: Configuration dictionary for the work cluster.
        """
        self.agents = agents
        self.duration_mean = config.get("duration_mean", 480)  # Default 8 hours
        self.duration_std = config.get("duration_std", 120)    # Default 2 hours
        self.min_links = config.get("min_links", 2)            # Minimum links per node

    def generate_graph(self):
        """
        Generate a Barabási-Albert graph for the work cluster.

        :return: A NetworkX graph representing the workplace.
        """
        graph = nx.barabasi_albert_graph(len(self.agents), self.min_links)
        for i, agent in enumerate(self.agents):
            graph.nodes[i]["agent"] = agent
        return graph

    def get_contact_duration(self):
        """
        Get the contact duration for this cluster.

        :return: Randomized contact duration based on configuration.
        """
        return max(0, random.gauss(self.duration_mean, self.duration_std))


class SchoolCluster:
    def __init__(self, agents, config):
        """
        Initialize a school cluster.

        :param agents: List of agents assigned to the school.
        :param config: Configuration dictionary for the school cluster.
        """
        self.agents = agents
        self.duration_mean = config.get("duration_mean", 300)  # Default 5 hours
        self.duration_std = config.get("duration_std", 60)     # Default 1 hour

    def generate_graph(self):
        """
        Generate a complete graph for the school cluster.

        :return: A NetworkX graph representing the school.
        """
        graph = nx.complete_graph(len(self.agents))
        for i, agent in enumerate(self.agents):
            graph.nodes[i]["agent"] = agent
        return graph

    def get_contact_duration(self):
        """
        Get the contact duration for this cluster.

        :return: Randomized contact duration based on configuration.
        """
        return max(0, random.gauss(self.duration_mean, self.duration_std))


class ShoppingCluster:
    def __init__(self, buyers, config):
        """
        Initialize a shopping cluster.

        :param buyers: List of agents designated as buyers.
        :param config: Configuration dictionary for the shopping cluster.
        """
        self.buyers = buyers
        self.duration_mean = config.get("duration_mean", 37)  # Default 37 minutes
        self.duration_std = config.get("duration_std", 10)    # Default 10 minutes
        self.max_agents = config.get("max_agents", 50)        # Max agents per shopping cluster

    def generate_graph(self):
        """
        Generate a complete graph for the shopping cluster with limited agents.

        :return: A NetworkX graph representing the shopping cluster.
        """
        sample_size = min(len(self.buyers), self.max_agents)
        sampled_buyers = random.sample(self.buyers, sample_size)
        graph = nx.complete_graph(len(sampled_buyers))
        for i, agent in enumerate(sampled_buyers):
            graph.nodes[i]["agent"] = agent
        return graph

    def get_contact_duration(self):
        """
        Get the contact duration for this cluster.

        :return: Randomized contact duration based on configuration.
        """
        return max(0, random.gauss(self.duration_mean, self.duration_std))


class TransportInteraction:
    def __init__(self, agents, config):
        """
        Initialize a transport interaction handler.

        :param agents: List of agents available for transport.
        :param config: Configuration dictionary for transport interactions.
        """
        self.agents = agents
        self.interval = config.get("interval", 5)  # Evaluation interval in minutes
        self.duration_mean = config.get("duration_mean", 15)  # Default contact duration mean
        self.duration_std = config.get("duration_std", 5)     # Default contact duration std

    def simulate_transport(self):
        """
        Simulate transport interactions among agents.

        :return: List of tuples representing agent interactions and their durations.
        """
        in_transit = random.sample(self.agents, k=min(len(self.agents), 50))  # Simulate up to 50 agents in transit
        interactions = []

        for i, agent1 in enumerate(in_transit):
            for agent2 in in_transit[i + 1:]:
                duration = max(0, random.gauss(self.duration_mean, self.duration_std))
                interactions.append((agent1, agent2, duration))

        return interactions

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
    # Example agents
    agents = [f"Agent_{i}" for i in range(100)]

    # Home cluster
    home_cluster = HomeCluster(agents[:5], example_config["home"])
    home_graph = home_cluster.generate_graph()
    print("Home Contact Duration:", home_cluster.get_contact_duration())

    # Work cluster
    work_cluster = WorkCluster(agents[5:30], example_config["work"])
    work_graph = work_cluster.generate_graph()
    print("Work Contact Duration:", work_cluster.get_contact_duration())

    # School cluster
    school_cluster = SchoolCluster(agents[30:50], example_config["school"])
    school_graph = school_cluster.generate_graph()
    print("School Contact Duration:", school_cluster.get_contact_duration())

    # Shopping cluster
    shopping_cluster = ShoppingCluster(agents[50:], example_config["shopping"])
    shopping_graph = shopping_cluster.generate_graph()
    print("Shopping Contact Duration:", shopping_cluster.get_contact_duration())

    # Transport interactions
    transport_interaction = TransportInteraction(agents, example_config["transport"])
    transport_results = transport_interaction.simulate_transport()
    print("Transport Interactions:", transport_results[:5])  # Print first 5 interactions
