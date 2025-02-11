from epidemics_sim.policies.base_policy import Policy

class LockdownPolicy(Policy):
    def __init__(self, restricted_clusters = ["work", "school"]):
        """
        Initialize the lockdown policy.

        :param restricted_clusters: List of cluster types to restrict (e.g., work, school).
        """
        self.restricted_clusters = restricted_clusters

    def enforce(self, agents, clusters):
        """
        Apply lockdown by restricting interactions in specific clusters.

        :param agents: List of agents in the simulation.
        :param clusters: Dictionary of clusters.
        """
        for cluster in clusters.values():
            if cluster.cluster_type in self.restricted_clusters:
                cluster.enforce_lockdown()

        # for cluster_type in self.restricted_clusters:
        #     if cluster_type in clusters:
        #         for subcluster in clusters[cluster_type].subclusters:
        #             subcluster.lockdown_active = True  # 🔒 Activar cuarentena en subclusters
        #             for agent in subcluster.agents:
        #                 agent.in_quarantine = True  # 🚨 Marcar a los agentes como en cuarentena

        print(f"🚨 Lockdown enforced on clusters: {self.restricted_clusters}")

    def delete(self, agents, clusters):
        """
        Apply lockdown by restricting interactions in specific clusters.

        :param agents: List of agents in the simulation.
        :param clusters: Dictionary of clusters.
        """
        for cluster in clusters.values():
            if cluster.cluster_type in self.restricted_clusters:
                cluster.remove_lockdown()

        # for cluster_type in self.restricted_clusters:
        #     if cluster_type in clusters:
        #         for subcluster in clusters[cluster_type].subclusters:
        #             subcluster.lockdown_active = True  # 🔒 Activar cuarentena en subclusters
        #             for agent in subcluster.agents:
        #                 agent.in_quarantine = True  # 🚨 Marcar a los agentes como en cuarentena

        print(f"🚨 Lockdown delete on clusters: {self.restricted_clusters}")

    def __str__(self):
        return "Lockdown Policy"
    
    def __repr__(self):
        return "Loackdown"