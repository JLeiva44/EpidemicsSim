import random
# Example Configuration
CONFIG = {
    "period_mapping": {
        "morning": ["home", "work"],
        "daytime": ["work", "shopping"],
        "evening": ["shopping", "home"],
        "night": ["home"]
    },
    "max_agents_in_transit": 50,
    "route_distribution": {
        "worker": [(["home", "work", "shopping", "home"], 1.0)],
        "student": [(["home", "school", "home"], 1.0)],
        "retired": [(["home"], 1.0)]
    }
}
class TransportInteraction:
    def __init__(self, agents, clusters, config= CONFIG):
        """
        Initialize a transport interaction handler.

        :param agents: List of agents available for transport.
        :param clusters: Dictionary of clusters (home, work, school, shopping).
        :param config: Configuration dictionary for transport interactions.
        """
        self.agents = agents
        self.clusters = clusters
        self.config = config
        self.routes = self._initialize_routes()

    def _initialize_routes(self):
        """
        Define movement routes for agents based on their roles (e.g., worker, student).

        :return: A dictionary mapping agents to their daily routes.
        """
        routes = {}
        route_distribution = self.config.get("route_distribution", {})
        for agent in self.agents:
            occupation_routes = route_distribution.get(agent.occupation, [(["home"], 1.0)])
            routes[agent] = random.choices(
                [route for route, _ in occupation_routes],
                [prob for _, prob in occupation_routes]
            )[0]
        return routes

    def simulate_transport(self, time_period):
        """
        Simulate transport interactions and agent movements for a specific time period.

        :param time_period: The time period (e.g., "morning", "daytime", "evening", "night").
        :return: List of movements and interactions.
        """
        interactions = []
        for agent, route in self.routes.items():
            # Determine relevant movement for the current time period
            period_routes = self._get_period_routes(route, time_period)
            for i in range(len(period_routes) - 1):
                origin = self.clusters.get(period_routes[i])
                destination = self.clusters.get(period_routes[i + 1])
                if origin and destination:  # Ensure clusters exist
                    interaction = self._simulate_single_transport(agent, origin, destination)
                    interactions.append(interaction)
        return interactions

    def _get_period_routes(self, route, time_period):
        """
        Map time periods to segments of the route.

        :param route: Full route of the agent.
        :param time_period: Current time period.
        :return: A subset of the route corresponding to the time period.
        """
        period_mapping = self.config.get("period_mapping", {
            "morning": ["home", "work"],
            "daytime": ["work", "shopping"],
            "evening": ["shopping", "home"],
            "night": ["home"]
        })
        return [stop for stop in route if stop in period_mapping.get(time_period, [])]

    def _simulate_single_transport(self, agent, origin_cluster, destination_cluster):
        """
        Simulate a single transport event for an agent.

        :param agent: The agent being transported.
        :param origin_cluster: The cluster the agent is leaving.
        :param destination_cluster: The cluster the agent is going to.
        :return: Interaction data for the transport event.
        """
        max_agents = self.config.get("max_agents_in_transit", 50)
        in_transit = random.sample(self.agents, k=min(len(self.agents), max_agents))
        interactions = []

        for other_agent in in_transit:
            if other_agent != agent:
                interactions.append((agent, other_agent))

        return {
            "agent": agent,
            "origin": origin_cluster,
            "destination": destination_cluster,
            "interactions": interactions
        }

# Example Configuration
CONFIG = {
    "period_mapping": {
        "morning": ["home", "work"],
        "daytime": ["work", "shopping"],
        "evening": ["shopping", "home"],
        "night": ["home"]
    },
    "max_agents_in_transit": 50,
    "route_distribution": {
        "worker": [(["home", "work", "shopping", "home"], 1.0)],
        "student": [(["home", "school", "home"], 1.0)],
        "retired": [(["home"], 1.0)]
    }
}

# # Example Usage
# if __name__ == "__main__":
#     # Example agents
#     class Agent:
#         def __init__(self, id, occupation):
#             self.id = id
#             self.occupation = occupation

#     agents = [Agent(f"Agent_{i}", random.choice(["worker", "student", "retired"])) for i in range(100)]

#     # Example clusters
#     clusters = {
#         "home": "HomeCluster",
#         "work": "WorkCluster",
#         "school": "SchoolCluster",
#         "shopping": "ShoppingCluster"
#     }

#     transport = TransportInteraction(agents, clusters, CONFIG)
#     morning_results = transport.simulate_transport("morning")
#     print("Morning Transport Interactions:", morning_results[:5])  # Print first 5 interactions
