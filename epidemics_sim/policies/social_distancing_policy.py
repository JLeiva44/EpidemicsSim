from epidemics_sim.policies.base_policy import Policy
import random

class SocialDistancingPolicy(Policy):
    def __init__(self, reduction_factor):
        """
        Initialize the social distancing policy.

        :param reduction_factor: Factor by which to reduce interactions (e.g., 0.5 for 50% reduction).
        """
        self.reduction_factor = reduction_factor

    def enforce(self, agents, clusters):
        """
        Apply social distancing by reducing edges in the interaction graphs.

        :param agents: List of agents in the simulation.
        :param clusters: Dictionary of clusters in the simulation.
        """
        for cluster_list in clusters.values():
            for cluster in cluster_list:
                graph = cluster.generate_graph()
                edges_to_remove = int(len(graph.edges) * (1 - self.reduction_factor))
                edges = list(graph.edges)
                random.shuffle(edges)
                for _ in range(edges_to_remove):
                    edge = edges.pop()
                    graph.remove_edge(*edge)


# class SocialDistancing(BasePolicy):
#     def __init__(self, reduction_factor):
#         """
#         Specific implementation of a social distancing policy.

#         :param reduction_factor: Factor by which interactions are reduced (0 to 1).
#         """
#         super().__init__(
#             name="Social Distancing",
#             description="Reduce the frequency of interactions between agents."
#         )
#         self.reduction_factor = reduction_factor

#     def apply(self, environment):
#         """
#         Apply social distancing by reducing interaction probabilities.

#         :param environment: An instance of BaseEnvironment or its subclasses.
#         """
#         for agent in environment.agents:
#             agent.attributes["interaction_reduction"] = self.reduction_factor
#         print(f"Social distancing applied to environment {environment.name} with reduction factor {self.reduction_factor}.")
