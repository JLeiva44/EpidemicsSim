class Policy:
    def enforce(self, agents, clusters):
        """
        Enforce the policy on agents and clusters.

        :param agents: List of agents in the simulation.
        :param clusters: Dictionary of clusters in the simulation.
        """
        raise NotImplementedError("This method should be implemented in subclasses.")

    def delete(self, agents, clusters):
        """
        Enforce the policy on agents and clusters.

        :param agents: List of agents in the simulation.
        :param clusters: Dictionary of clusters in the simulation.
        """
        raise NotImplementedError("This method should be implemented in subclasses.")

    def __str__(self):
        return "Lockdown Policy"
