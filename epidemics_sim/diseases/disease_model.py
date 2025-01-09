import random

class DiseaseModel:
    def __init__(self, agents, transmission_rate, recovery_rate, mortality_rate):
        """
        Base class for disease models.

        :param agents: List of agents in the simulation.
        :param transmission_rate: Probability of transmission per contact.
        :param recovery_rate: Probability of recovery per day.
        :param mortality_rate: Probability of death if in critical condition.
        """
        self.agents = agents
        self.transmission_rate = transmission_rate
        self.recovery_rate = recovery_rate
        self.mortality_rate = mortality_rate

    def propagate(self, daily_interactions):
        """
        Handle the propagation of the disease based on interactions.

        :param daily_interactions: Dictionary of daily interactions by time intervals.
        """
        for time_interval, interactions in daily_interactions.items():
            for graph, duration in interactions:
                self._evaluate_transmission(graph, duration)

    def _evaluate_transmission(self, graph, duration):
        """
        Evaluate transmission of the disease in a graph.

        :param graph: Interaction graph.
        :param duration: Duration of the contact.
        """
        for edge in graph.edges:
            agent1 = graph.nodes[edge[0]]['agent']
            agent2 = graph.nodes[edge[1]]['agent']

            if agent1.is_infected and agent2.infection_status["state"] == "susceptible" and not agent2.immune:
                self._attempt_infection(agent2, duration)

            elif agent2.is_infected and agent1.infection_status["state"] == "susceptible" and not agent1.immune:
                self._attempt_infection(agent1, duration)

    def _attempt_infection(self, agent, duration):
        """
        Attempt to infect an agent based on contact duration.

        :param agent: Susceptible agent.
        :param duration: Duration of contact.
        """
        probability = self.transmission_rate * (duration / 60)
        if random.random() < probability:
            agent.infection_status["state"] = "infected"

    def update_states(self):
        """
        Update the state of all agents, progressing infections.
        """
        for agent in self.agents:
            if agent.is_infected:
                agent.progress_infection(self._determine_severity, self.mortality_rate)

    def _determine_severity(self):
        """
        Determine the severity of the disease for an infected agent.

        :return: Severity level ('mild', 'moderate', 'severe', 'critical').
        """
        severity_levels = ["mild", "moderate", "severe", "critical"]
        probabilities = [0.6, 0.25, 0.1, 0.05]
        return random.choices(severity_levels, probabilities)[0]
