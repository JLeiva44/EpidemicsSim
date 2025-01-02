import random
import networkx as nx

#TODO mortalityreate?
class DiseaseModel:
    def __init__(self, transmission_rate, recovery_rate, states):
        """
        Base model for disease propagation.

        :param transmission_rate: Probability of disease transmission per contact.
        :param recovery_rate: Probability of recovery per day.
        :param states: List of possible health states (e.g., susceptible, infected, recovered).
        """
        self.transmission_rate = transmission_rate
        self.recovery_rate = recovery_rate
        self.states = states

    def propagate(self, daily_interactions):
        """
        Propagate the disease based on daily interactions.

        :param daily_interactions: Dictionary of interactions per cluster.
        """
        for cluster_type, interactions in daily_interactions.items():
            for graph, duration in interactions:
                self._process_graph(graph, duration)

    def update_states(self):
        """
        Update agent health states (e.g., recover infected agents).
        """
        raise NotImplementedError("This method should be implemented in subclasses.")

    def _process_graph(self, graph, duration):
        """
        Process interactions within a graph to propagate the disease.

        :param graph: A NetworkX graph representing interactions.
        :param duration: Duration of interactions in the graph.
        """
        for edge in graph.edges:
            agent1 = graph.nodes[edge[0]]['agent']
            agent2 = graph.nodes[edge[1]]['agent']
            self._evaluate_transmission(agent1, agent2, duration)

    def _evaluate_transmission(self, agent1, agent2, duration):
        """
        Evaluate transmission between two agents based on their states and contact duration.

        :param agent1: First agent in the interaction.
        :param agent2: Second agent in the interaction.
        :param duration: Duration of the contact.
        """
        raise NotImplementedError("This method should be implemented in subclasses.")



# class BaseDisease:
#     def __init__(self, name, transmission_rate, recovery_rate, mortality_rate):
#         """
#         Base class for diseases in the simulation.

#         :param name: Name of the disease.
#         :param transmission_rate: Probability of disease transmission per interaction.
#         :param recovery_rate: Probability of recovery per time step.
#         :param mortality_rate: Probability of death per time step for infected agents.
#         """
#         self.name = name
#         self.transmission_rate = transmission_rate
#         self.recovery_rate = recovery_rate
#         self.mortality_rate = mortality_rate

#     def __repr__(self):
#         return (
#             f"BaseDisease(name={self.name}, transmission_rate={self.transmission_rate}, "
#             f"recovery_rate={self.recovery_rate}, mortality_rate={self.mortality_rate})"
#         )
