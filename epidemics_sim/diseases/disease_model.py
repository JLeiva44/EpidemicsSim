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


# import random

# class DiseaseModel:
#     def __init__(self, agents, transmission_rate, base_recovery_rate, base_mortality_rate):
#         """
#         Base class for disease models.

#         :param agents: List of agents in the simulation.
#         :param transmission_rate: Probability of transmission per contact.
#         :param base_recovery_rate: Base probability of recovery per day.
#         :param base_mortality_rate: Base probability of death if in critical condition.
#         """
#         self.agents = agents
#         self.transmission_rate = transmission_rate
#         self.base_recovery_rate = base_recovery_rate
#         self.base_mortality_rate = base_mortality_rate

#     def propagate(self, daily_interactions):
#         """
#         Handle the propagation of the disease based on interactions.

#         :param daily_interactions: Dictionary of daily interactions by time intervals.
#         """
#         for time_interval, interactions in daily_interactions.items():
#             for interaction in interactions:
#                 self._evaluate_transmission(interaction)

#     def _evaluate_transmission(self, interaction):
#         """
#         Evaluate transmission based on contact.

#         :param interaction: Dictionary containing 'agent1', 'agent2', and 'has_contact'.
#         """
#         agent1 = interaction['agent1']
#         agent2 = interaction['agent2']
#         has_contact = interaction['has_contact']

#         if has_contact:
#             if agent1.is_infected and agent2.infection_status["state"] == "susceptible" and not agent2.immune:
#                 self._attempt_infection(agent2)

#             elif agent2.is_infected and agent1.infection_status["state"] == "susceptible" and not agent1.immune:
#                 self._attempt_infection(agent1)

#     def _attempt_infection(self, agent):
#         """
#         Attempt to infect an agent.

#         :param agent: Susceptible agent.
#         """
#         if random.random() < self.transmission_rate:
#             agent.infection_status["state"] = "infected"

#     def update_states(self, healthcare_system):
#         """
#         Update the state of all agents, progressing infections.

#         :param healthcare_system: The healthcare system managing the agents.
#         """
#         for agent in self.agents:
#             if agent.is_infected:
#                 care_level = healthcare_system.get_care_level(agent)
#                 recovery_rate, mortality_rate = self._adjust_rates(care_level)
#                 agent.progress_infection(self._determine_severity, recovery_rate, mortality_rate)

#     def _adjust_rates(self, care_level):
#         """
#         Adjust recovery and mortality rates based on the level of care.

#         :param care_level: The level of care ('consultorio', 'policlinico', 'hospital').
#         :return: Tuple (adjusted_recovery_rate, adjusted_mortality_rate).
#         """
#         adjustments = {
#             "consultorio": (1.0, 1.2),
#             "policlinico": (1.2, 1.0),
#             "hospital": (1.5, 0.8)
#         }
#         factor_recovery, factor_mortality = adjustments.get(care_level, (1.0, 1.0))
#         return self.base_recovery_rate * factor_recovery, self.base_mortality_rate * factor_mortality

#     def _determine_severity(self):
#         """
#         Determine the severity of the disease for an infected agent.

#         :return: Severity level ('mild', 'moderate', 'severe', 'critical').
#         """
#         severity_levels = ["mild", "moderate", "severe", "critical"]
#         probabilities = [0.6, 0.25, 0.1, 0.05]
#         return random.choices(severity_levels, probabilities)[0]


# # import random

# # class DiseaseModel:
# #     def __init__(self, agents, transmission_rate, recovery_rate, mortality_rate):
# #         """
# #         Base class for disease models.

# #         :param agents: List of agents in the simulation.
# #         :param transmission_rate: Probability of transmission per contact.
# #         :param recovery_rate: Probability of recovery per day.
# #         :param mortality_rate: Probability of death if in critical condition.
# #         """
# #         self.agents = agents
# #         self.transmission_rate = transmission_rate
# #         self.recovery_rate = recovery_rate
# #         self.mortality_rate = mortality_rate

# #     def propagate(self, daily_interactions):
# #         """
# #         Handle the propagation of the disease based on interactions.

# #         :param daily_interactions: Dictionary of daily interactions by time intervals.
# #         """
# #         for time_interval, interactions in daily_interactions.items():
# #             for graph, duration in interactions:
# #                 self._evaluate_transmission(graph, duration)

# #     def _evaluate_transmission(self, graph, duration):
# #         """
# #         Evaluate transmission of the disease in a graph.

# #         :param graph: Interaction graph.
# #         :param duration: Duration of the contact.
# #         """
# #         for edge in graph.edges:
# #             agent1 = graph.nodes[edge[0]]['agent']
# #             agent2 = graph.nodes[edge[1]]['agent']

# #             if agent1.is_infected and agent2.infection_status["state"] == "susceptible" and not agent2.immune:
# #                 self._attempt_infection(agent2, duration)

# #             elif agent2.is_infected and agent1.infection_status["state"] == "susceptible" and not agent1.immune:
# #                 self._attempt_infection(agent1, duration)

# #     def _attempt_infection(self, agent, duration):
# #         """
# #         Attempt to infect an agent based on contact duration.

# #         :param agent: Susceptible agent.
# #         :param duration: Duration of contact.
# #         """
# #         probability = self.transmission_rate * (duration / 60)
# #         if random.random() < probability:
# #             agent.infection_status["state"] = "infected"

# #     def update_states(self):
# #         """
# #         Update the state of all agents, progressing infections.
# #         """
# #         for agent in self.agents:
# #             if agent.is_infected:
# #                 agent.progress_infection(self._determine_severity, self.mortality_rate)

# #     def _determine_severity(self):
# #         """
# #         Determine the severity of the disease for an infected agent.

# #         :return: Severity level ('mild', 'moderate', 'severe', 'critical').
# #         """
# #         severity_levels = ["mild", "moderate", "severe", "critical"]
# #         probabilities = [0.6, 0.25, 0.1, 0.05]
# #         return random.choices(severity_levels, probabilities)[0]
