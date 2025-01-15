from .disease_model import DiseaseModel
import random
class CovidModel(DiseaseModel):
    def __init__(self, agents, transmission_rate, recovery_rate, mortality_rate):
        """
        Model specific to COVID-19.

        :param agents: List of agents in the simulation.
        :param transmission_rate: Probability of transmission per contact.
        :param recovery_rate: Probability of recovery per day.
        :param mortality_rate: Probability of death per day for infected agents.
        """
        super().__init__(agents, transmission_rate, recovery_rate, mortality_rate)

    def update_states(self):
        """
        Update agent health states for COVID-19, including mortality and recovery.
        """
        for agent in self.agents:
            if agent.infection_status["state"] == "infected":
                # Evaluate severity for new infections
                if agent.days_infected == 0:
                    agent.infection_status["severity"] = self._determine_severity(agent)

                # Progress infection state
                agent.days_infected += 1

                # Evaluate mortality for critical cases
                if agent.infection_status["severity"] == "critical":
                    mortality_chance = self.mortality_rate
                    if random.random() < mortality_chance:
                        agent.infection_status["state"] = "deceased"
                        continue

                # Evaluate recovery for non-deceased cases
                if random.random() < self.recovery_rate:
                    agent.infection_status["state"] = "recovered"
                    agent.immune = True

    def _evaluate_transmission(self, graph, duration):
        """
        Evaluate transmission in a graph.

        :param graph: Interaction graph.
        :param duration: Duration of contact.
        """
        for edge in graph.edges:
            agent1 = graph.nodes[edge[0]]['agent']
            agent2 = graph.nodes[edge[1]]['agent']
            self._attempt_transmission(agent1, agent2, duration)
            self._attempt_transmission(agent2, agent1, duration)

    def _attempt_transmission(self, source, target, duration):
        """
        Attempt transmission from one agent to another.

        :param source: Source agent.
        :param target: Target agent.
        :param duration: Duration of contact.
        """
        if target.infection_status["state"] == "susceptible" and not target.immune:
            transmission_probability = self.transmission_rate

            # Adjust for vaccination and mask usage
            if target.vaccinated:
                transmission_probability *= 0.5
            if source.mask_usage or target.mask_usage:
                transmission_probability *= 0.7

            # Superpropagators increase risk
            if source.is_superpropagator:
                transmission_probability *= 1.5

            # Adjust for contact duration
            transmission_probability *= duration / 60

            if random.random() < transmission_probability:
                target.infection_status["state"] = "infected"

    def _determine_severity(self, agent):
        """
        COVID-19 specific severity determination considering comorbidities and other factors.

        :param agent: The agent whose severity is being determined.
        :return: Severity level ('mild', 'moderate', 'severe', 'critical').
        """
        severity_levels = ["mild", "moderate", "severe", "critical"]
        probabilities = [0.8, 0.15, 0.04, 0.01]

        # Adjust probabilities based on comorbidities
        if "diabetes" in agent.comorbidities:
            probabilities[2] += 0.02  # Increase severe probability
        if "obesity" in agent.comorbidities:
            probabilities[1] += 0.03  # Increase moderate probability
        if "hypertension" in agent.comorbidities:
            probabilities[2] += 0.03  # Increase severe probability
        if "heart_disease" in agent.comorbidities:
            probabilities[3] += 0.04  # Increase critical probability
        if "cancer" in agent.comorbidities:
            probabilities[3] += 0.05  # Increase critical probability
        if "chronic_respiratory" in agent.comorbidities:
            probabilities[2] += 0.03  # Increase severe probability
        if agent.age > 60:
            probabilities[3] += 0.03  # Increase critical probability

        return random.choices(severity_levels, probabilities)[0]

    def apply_isolation(self, agents_to_isolate):
        """
        Mark agents as isolated, preventing them from interacting with others.

        :param agents_to_isolate: List of agents to isolate.
        """
        for agent in agents_to_isolate:
            agent.isolated = True
# class CovidModel(DiseaseModel):
#     def __init__(self, agents, transmission_rate, recovery_rate, mortality_rate):
#         """
#         Model specific to COVID-19.

#         :param agents: List of agents in the simulation.
#         :param transmission_rate: Probability of transmission per contact.
#         :param recovery_rate: Probability of recovery per day.
#         :param mortality_rate: Probability of death per day for infected agents.
#         """
#         super().__init__(agents, transmission_rate, recovery_rate, mortality_rate)

#     def update_states(self):
#         """
#         Update agent health states for COVID-19, including mortality and recovery.
#         """
#         for agent in self.agents:
#             if agent.infection_status["state"] == "infected":
#                 # Evaluate mortality
#                 mortality_chance = self.mortality_rate
#                 if agent.age > 60:
#                     mortality_chance *= 1.5
#                 if "diabetes" in agent.comorbidities:
#                     mortality_chance *= 1.3

#                 if random.random() < mortality_chance:
#                     agent.infection_status["state"] = "deceased"
#                     continue

#                 # Evaluate recovery
#                 if random.random() < self.recovery_rate:
#                     agent.infection_status["state"] = "recovered"
#                     agent.immune = True

#     def _evaluate_transmission(self, graph, duration):
#         """
#         Evaluate transmission in a graph.

#         :param graph: Interaction graph.
#         :param duration: Duration of contact.
#         """
#         for edge in graph.edges:
#             agent1 = graph.nodes[edge[0]]['agent']
#             agent2 = graph.nodes[edge[1]]['agent']
#             self._attempt_transmission(agent1, agent2, duration)
#             self._attempt_transmission(agent2, agent1, duration)

#     def _attempt_transmission(self, source, target, duration):
#         """
#         Attempt transmission from one agent to another.

#         :param source: Source agent.
#         :param target: Target agent.
#         :param duration: Duration of contact.
#         """
#         if target.infection_status["state"] == "susceptible" and not target.immune:
#             transmission_probability = self.transmission_rate
#             if target.vaccinated:
#                 transmission_probability *= 0.5
#             if source.mask_usage or target.mask_usage:
#                 transmission_probability *= 0.7
#             transmission_probability *= duration / 60

#             if random.random() < transmission_probability:
#                 target.infection_status["state"] = "infected"

#     def _determine_severity(self):
#         """
#         COVID-19 specific severity determination.

#         :return: Severity level ('mild', 'moderate', 'severe', 'critical').
#         """
#         severity_levels = ["mild", "moderate", "severe", "critical"]
#         probabilities = [0.8, 0.15, 0.04, 0.01]
#         return random.choices(severity_levels, probabilities)[0]
