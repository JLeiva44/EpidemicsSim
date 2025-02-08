import random
import networkx as nx
import numpy as np

class Subcluster:
    def __init__(self, agents, topology="scale_free", interaction_probability=0.7):
        self.agents = agents
        self.topology = topology
        self.interaction_probability = interaction_probability
        self.graph = self._generate_graph()
        self.contact_matrix = self._generate_contact_matrix()
    
    def _generate_graph(self):
        """
        Generate a network graph based on the specified topology.
        """
        num_agents = len(self.agents)
        if num_agents < 2:
            return nx.Graph()
        
        if self.topology == "scale_free":
            m = max(1, min(2, num_agents - 1))
            graph = nx.barabasi_albert_graph(num_agents, m)
        elif self.topology == "complete":
            graph = nx.complete_graph(num_agents)
        else:
            raise ValueError(f"Unknown topology: {self.topology}")
        
        for i, agent in enumerate(self.agents):
            graph.nodes[i]["agent"] = agent
        
        return graph
    
    def _generate_contact_matrix(self):
        """
        Generate a contact matrix from the network graph.
        """
        num_agents = len(self.agents)
        matrix = np.zeros((num_agents, num_agents))
        
        for i, j in self.graph.edges():
            if random.random() < self.interaction_probability:
                matrix[i, j] = matrix[j, i] = 1
        
        return matrix

    def remove_deceased_agents(self):
        """
        Remove deceased agents from the subcluster and update the graph and matrix.
        """
        self.agents = [agent for agent in self.agents if agent.is_alive]
        self.graph = self._generate_graph()
        self.contact_matrix = self._generate_contact_matrix()

    def simulate_interactions(self):
        """
        Simulate interactions using the contact matrix, ignoring isolated and hospitalized agents.
        """
        interactions = []
        for i, agent1 in enumerate(self.agents):
            if agent1.is_hospitalized or agent1.is_isolated:
                continue  # Skip agents who shouldn't interact
            for j, agent2 in enumerate(self.agents):
                if i != j and self.contact_matrix[i, j] == 1:
                    interactions.append((agent1, agent2))
        return interactions

class ClusterWithSubclusters:
    def __init__(self, subclusters, cluster_type, active_periods):
        self.subclusters = subclusters
        self.cluster_type = cluster_type
        self.active_periods = active_periods
        self.lockdown_is_active = False

    def enforce_lockdown(self):
        self.lockdown_is_active = True
    
    def remove_lockdown(self):
        self.lockdown_is_active = False

    def remove_deceased_agents(self):
        for subcluster in self.subclusters:
            subcluster.remove_deceased_agents()

    def simulate_interactions(self, time_period):
        interactions = []
        if not self.lockdown_is_active and time_period in self.active_periods:
            for subcluster in self.subclusters:
                interactions.extend(subcluster.simulate_interactions())
        return interactions
