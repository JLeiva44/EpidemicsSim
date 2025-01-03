import random
import networkx as nx
from epidemics_sim.logger import logger

class DiseaseModel:
    def __init__(self, agents, transmission_rate, recovery_rate, mortality_rate, states):
        """
        Base model for disease propagation.

        :param agents: List of agents in the simulation.
        :param transmission_rate: Probability of disease transmission per contact.
        :param recovery_rate: Probability of recovery per day.
        :param mortality_rate: Base probability of death per day for infected agents.
        :param states: List of possible health states (e.g., susceptible, infected, recovered, deceased).
        """
        self.agents = agents
        self.transmission_rate = transmission_rate
        self.recovery_rate = recovery_rate
        self.mortality_rate = mortality_rate
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
        Update agent health states, including recovery and mortality.
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


# def propagate(self, daily_interactions):
    #     """
    #     Propagate the disease based on daily interactions.

    #     :param daily_interactions: Dictionary of interactions per cluster.
    #     """
    #     for cluster_type, interactions in daily_interactions.items():
    #         logger.debug(interactions)
    #         for interaction in interactions:
    #             if isinstance(interaction, tuple) and len(interaction) == 2:
    #                 graph, duration = interaction
    #                 self._process_graph(graph, duration)
    #             else:
    #                 logger.error(f"Invalid interaction format: {interaction}")

