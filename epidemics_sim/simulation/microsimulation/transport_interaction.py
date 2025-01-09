import random

class TransportInteraction:
    def __init__(self, agents, clusters, config):
        """
        Initialize a transport interaction handler.

        :param agents: List of agents available for transport.
        :param clusters: Dictionary of clusters (home, work, school, shopping).
        :param config: Configuration dictionary for transport interactions.
        """
        self.agents = agents
        self.clusters = clusters
        self.config = config
        self.duration_mean = config.get("duration_mean", 15)
        self.duration_std = config.get("duration_std", 5)
        self.routes = self._initialize_routes()

    def _initialize_routes(self):
        """
        Define movement routes for agents based on their roles (e.g., worker, student).

        :return: A dictionary mapping agents to their daily routes.
        """
        routes = {}
        for agent in self.agents:
            if agent.occupation == "worker":
                routes[agent] = ["home", "work", "shopping", "home"]
            elif agent.occupation == "student":
                routes[agent] = ["home", "school", "home"]
            else:
                routes[agent] = ["home"]
        return routes

    def simulate_transport(self):
        """
        Simulate transport interactions and agent movements.

        :return: List of movements and interactions.
        """
        interactions = []
        for agent, route in self.routes.items():
            for i in range(len(route) - 1):
                origin = self.clusters[route[i]]
                destination = self.clusters[route[i + 1]]
                interaction = self._simulate_single_transport(agent, origin, destination)
                interactions.append(interaction)
        return interactions

    def _simulate_single_transport(self, agent, origin_cluster, destination_cluster):
        """
        Simulate a single transport event for an agent.

        :param agent: The agent being transported.
        :param origin_cluster: The cluster the agent is leaving.
        :param destination_cluster: The cluster the agent is going to.
        :return: Interaction data for the transport event.
        """
        in_transit = random.sample(self.agents, k=min(len(self.agents), 50))
        duration = max(0, random.gauss(self.duration_mean, self.duration_std))
        interactions = []

        for other_agent in in_transit:
            if other_agent != agent:
                interactions.append((agent, other_agent, duration))

        return {
            "agent": agent,
            "origin": origin_cluster,
            "destination": destination_cluster,
            "interactions": interactions
        }

# Example usage
if __name__ == "__main__":
    # Example agents
    agents = [f"Agent_{i}" for i in range(100)]

    # Example clusters
    clusters = {
        "home": "HomeCluster",
        "work": "WorkCluster",
        "school": "SchoolCluster",
        "shopping": "ShoppingCluster"
    }

    # Example config
    config = {
        "duration_mean": 15,
        "duration_std": 5
    }

    transport = TransportInteraction(agents, clusters, config)
    transport_results = transport.simulate_transport()
    print("Transport Interactions:", transport_results[:5])  # Print first 5 interactions
