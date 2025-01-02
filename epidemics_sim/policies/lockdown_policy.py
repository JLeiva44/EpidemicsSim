from epidemics_sim.policies.base_policy import Policy

class LockdownPolicy(Policy):
    def __init__(self, restricted_clusters):
        """
        Initialize the lockdown policy.

        :param restricted_clusters: List of cluster types to restrict (e.g., work, school).
        """
        self.restricted_clusters = restricted_clusters

    def enforce(self, agents, clusters):
        """
        Apply lockdown by disabling interactions in specific clusters.

        :param agents: List of agents in the simulation.
        :param clusters: Dictionary of clusters in the simulation.
        """
        for cluster_type in self.restricted_clusters:
            if cluster_type in clusters:
                clusters[cluster_type] = []
        print(f"Lockdown enforced on clusters: {self.restricted_clusters}.")





# class Lockdown(BasePolicy):
#     def __init__(self):
#         """
#         Specific implementation of a lockdown policy.
#         """
#         super().__init__(
#             name="Lockdown",
#             description="Restrict movement of agents to reduce interactions."
#         )

#     def apply(self, environment):
#         """
#         Apply lockdown by restricting agent movements in the environment.

#         :param environment: An instance of BaseEnvironment or its subclasses.
#         """
#         for agent in environment.agents:
#             agent.attributes["movement_restricted"] = True
#         print(f"Lockdown applied to environment {environment.name}.")
