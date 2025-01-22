import random
from epidemics_sim.simulation.clusters import CityClusterGenerator
from epidemics_sim.simulation.healthcare import HealthcareSystem
from epidemics_sim.simulation.simulation_utils import SimulationAnalyzer

class DailySimulation:
    def __init__(self, agents, cluster_generator, transport, config, disease_model, policies, healthcare_system, analyzer, initial_infected=50):
        """
        Initialize the daily simulation controller.

        :param agents: List of agents in the simulation.
        :param cluster_generator: Instance of CityClusterGenerator to create clusters dynamically.
        :param transport: Transport interaction handler.
        :param config: Configuration dictionary for the simulation.
        :param disease_model: Model handling the disease propagation.
        :param policies: List of active health policies.
        :param healthcare_system: Instance of the HealthcareSystem to manage healthcare.
        :param analyzer: Instance of SimulationAnalyzer to track statistics.
        :param initial_infected: Number of agents to infect at the start of the simulation.
        """
        self.agents = agents
        self.cluster_generator = cluster_generator
        self.transport = transport
        self.config = config
        self.disease_model = disease_model
        self.policies = policies
        self.healthcare_system = healthcare_system
        self.analyzer = analyzer
        self.clusters = self.cluster_generator.generate_clusters(self.agents)

        # Initialize infections
        self._initialize_infections(initial_infected)

    def _initialize_infections(self, initial_infected):
        """
        Infect a specified number of agents at the start of the simulation.

        :param initial_infected: Number of agents to infect initially.
        """
        infected_agents = random.sample(self.agents, initial_infected)
        for agent in infected_agents:
            agent.infection_status["state"] = "infected"
            agent.days_infected = 0

    def simulate(self, days):
        """
        Simulate interactions over multiple days.

        :param days: Number of days to simulate.
        :return: Summary of interactions and disease progression over the simulation period.
        """
        simulation_results = []

        for day in range(days):
            print(f"Simulating Day {day + 1}...")
            daily_summary = self.simulate_day()
            simulation_results.append(daily_summary)

            # Update disease progression based on daily interactions
            self.disease_model.update_states(self.agents)

            # Notify the healthcare system about new infections or changes
            for agent in self.agents:
                if agent.is_infected and not self.healthcare_system.is_registered(agent):
                    self.healthcare_system.notify_infection(agent)

            # Perform daily healthcare operations
            self.healthcare_system.daily_operations()

            # Record daily statistics
            self.analyzer.record_daily_stats(self.agents)

        # Generate and plot the final report
        report = self.analyzer.generate_report()
        self.analyzer.plot_disease_progression()

        return simulation_results

    def simulate_day(self):
        """
        Simulate a single day of interactions, ordered by time intervals.

        :return: A summary of interactions for the day.
        """
        daily_interactions = {
            "morning": self._simulate_morning(),
            "daytime": self._simulate_daytime(),
            "evening": self._simulate_evening(),
            "night": self._simulate_night()
        }

        # Propagate disease based on interactions
        self.disease_model.propagate(daily_interactions)

        return daily_interactions

    def _simulate_morning(self):
        """
        Simulate interactions in the morning: Home and transport.

        :return: A list of interactions for the morning.
        """
        interactions = []
        interactions.extend(self._simulate_cluster_interactions(self.clusters["home"], "morning"))
        interactions.extend(self.transport.simulate_transport("morning"))
        return interactions

    def _simulate_daytime(self):
        """
        Simulate interactions during the day: Work and school.

        :return: A list of interactions for the daytime.
        """
        interactions = []
        interactions.extend(self._simulate_cluster_interactions(self.clusters["work"], "daytime"))
        interactions.extend(self._simulate_cluster_interactions(self.clusters["school"], "daytime"))
        return interactions

    def _simulate_evening(self):
        """
        Simulate interactions in the evening: Transport and shopping.

        :return: A list of interactions for the evening.
        """
        interactions = []
        interactions.extend(self.transport.simulate_transport("evening"))
        interactions.extend(self._simulate_cluster_interactions(self.clusters["shopping"], "evening"))
        return interactions

    def _simulate_night(self):
        """
        Simulate interactions at night: Home only.

        :return: A list of interactions for the night.
        """
        return self._simulate_cluster_interactions(self.clusters["home"], "night")

    def _simulate_cluster_interactions(self, cluster, time_period):
        """
        Simulate interactions within a cluster and its subclusters for a specific time period.

        :param cluster: A ClusterWithSubclusters instance.
        :param time_period: Current time period.
        :return: List of interactions within the cluster and subclusters.
        """
        return cluster.simulate_interactions(time_period)

    def _apply_policies(self):
        """
        Apply health policies to modify agent behavior or cluster interactions.
        """
        for policy in self.policies:
            policy.enforce(self.agents, self.clusters)
