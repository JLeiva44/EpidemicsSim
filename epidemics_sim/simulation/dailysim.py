import random
from city_cluster_generator import CityClusterGenerator
from healthcare_system import HealthcareSystem
from simulation_analyzer import SimulationAnalyzer

class DailySimulation:
    def __init__(self, agents, cluster_generator, transport, config, disease_model, policies, healthcare_system, analyzer, initial_infected=1):
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
        self.clusters = self._generate_clusters()

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

    def _generate_clusters(self):
        """
        Generate clusters dynamically using the cluster generator.

        :return: A dictionary of generated clusters.
        """
        home_clusters = self.cluster_generator.generate_home_clusters(self.agents)
        work_clusters = self.cluster_generator.generate_work_clusters(self.agents[:len(self.agents) // 2])
        school_clusters = self.cluster_generator.generate_school_clusters(self.agents[len(self.agents) // 2:])
        shopping_clusters = self.cluster_generator.generate_shopping_clusters(self.agents)

        return {
            "home": home_clusters,
            "work": work_clusters,
            "school": school_clusters,
            "shopping": shopping_clusters
        }

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
            self.disease_model.update_states()

            # Notify the healthcare system about new infections or changes
            for agent in self.agents:
                if agent.is_infected and not self.healthcare_system.is_registered(agent):
                    self.healthcare_system.notify_infection(agent)

            # Perform daily healthcare operations
            self.healthcare_system.daily_operations()

            # Record daily statistics
            self.analyzer.record_daily_stats(self.agents, self.healthcare_system)

        # Generate and plot the final report
        report = self.analyzer.generate_report()
        self.analyzer.plot_statistics()

        return simulation_results

    def simulate_day(self):
        """
        Simulate a single day of interactions, ordered by time intervals.

        :return: A summary of interactions for the day.
        """
        daily_interactions = {
            "6-8am": self._simulate_morning(),
            "8am-5pm": self._simulate_daytime(),
            "5-8pm": self._simulate_evening(),
            "8pm-6am": self._simulate_night()
        }

        # Propagate disease based on interactions
        self.disease_model.propagate(daily_interactions)

        return daily_interactions

    def _simulate_morning(self):
        """
        Simulate interactions in the morning (6-8am): Home and transport.

        :return: A list of interactions for the morning.
        """
        interactions = []
        interactions.extend(self._simulate_cluster_interactions(self.clusters["home"]))
        interactions.extend(self.transport.simulate_transport("morning"))
        return interactions

    def _simulate_daytime(self):
        """
        Simulate interactions during the day (8am-5pm): Work and school.

        :return: A list of interactions for the daytime.
        """
        interactions = []
        interactions.extend(self._simulate_cluster_interactions(self.clusters["work"]))
        interactions.extend(self._simulate_cluster_interactions(self.clusters["school"]))
        return interactions

    def _simulate_evening(self):
        """
        Simulate interactions in the evening (5-8pm): Transport and shopping.

        :return: A list of interactions for the evening.
        """
        interactions = []
        interactions.extend(self.transport.simulate_transport("evening"))
        interactions.extend(self._simulate_cluster_interactions(self.clusters["shopping"]))
        return interactions

    def _simulate_night(self):
        """
        Simulate interactions at night (8pm-6am): Home only.

        :return: A list of interactions for the night.
        """
        return self._simulate_cluster_interactions(self.clusters["home"])

    def _simulate_cluster_interactions(self, cluster_list):
        """
        Simulate interactions within a list of clusters and their subclusters.

        :param cluster_list: List of clusters to simulate.
        :return: List of interactions within the clusters and subclusters.
        """
        interactions = []
        for cluster in cluster_list:
            subcluster_interactions = cluster.simulate_interactions()
            interactions.extend(subcluster_interactions)
        return interactions

    def _apply_policies(self):
        """
        Apply health policies to modify agent behavior or cluster interactions.
        """
        for policy in self.policies:
            policy.enforce(self.agents, self.clusters)


# import random
# from city_cluster_generator import CityClusterGenerator
# from healthcare_system import HealthcareSystem
# from simulation_analyzer import SimulationAnalyzer

# class DailySimulation:
#     def __init__(self, agents, cluster_generator, transport, config, disease_model, policies, healthcare_system, analyzer):
#         """
#         Initialize the daily simulation controller.

#         :param agents: List of agents in the simulation.
#         :param cluster_generator: Instance of CityClusterGenerator to create clusters dynamically.
#         :param transport: Transport interaction handler.
#         :param config: Configuration dictionary for the simulation.
#         :param disease_model: Model handling the disease propagation.
#         :param policies: List of active health policies.
#         :param healthcare_system: Instance of the HealthcareSystem to manage healthcare.
#         :param analyzer: Instance of SimulationAnalyzer to track statistics.
#         """
#         self.agents = agents
#         self.cluster_generator = cluster_generator
#         self.transport = transport
#         self.config = config
#         self.disease_model = disease_model
#         self.policies = policies
#         self.healthcare_system = healthcare_system
#         self.analyzer = analyzer
#         self.clusters = self._generate_clusters()

#     def _generate_clusters(self):
#         """
#         Generate clusters dynamically using the cluster generator.

#         :return: A dictionary of generated clusters.
#         """
#         home_clusters = self.cluster_generator.generate_home_clusters(self.agents)
#         work_clusters = self.cluster_generator.generate_work_clusters(self.agents[:len(self.agents) // 2])
#         school_clusters = self.cluster_generator.generate_school_clusters(self.agents[len(self.agents) // 2:])
#         shopping_clusters = self.cluster_generator.generate_shopping_clusters(self.agents)

#         return {
#             "home": home_clusters,
#             "work": work_clusters,
#             "school": school_clusters,
#             "shopping": shopping_clusters
#         }

#     def simulate(self, days):
#         """
#         Simulate interactions over multiple days.

#         :param days: Number of days to simulate.
#         :return: Summary of interactions and disease progression over the simulation period.
#         """
#         simulation_results = []

#         for day in range(days):
#             print(f"Simulating Day {day + 1}...")
#             daily_summary = self.simulate_day()
#             simulation_results.append(daily_summary)

#             # Update disease progression based on daily interactions
#             self.disease_model.update_states()

#             # Notify the healthcare system about new infections or changes
#             for agent in self.agents:
#                 if agent.is_infected and not self.healthcare_system.is_registered(agent):
#                     self.healthcare_system.notify_infection(agent)

#             # Perform daily healthcare operations
#             self.healthcare_system.daily_operations()

#             # Record daily statistics
#             self.analyzer.record_daily_stats(self.agents, self.healthcare_system)

#         # Generate and plot the final report
#         report = self.analyzer.generate_report()
#         self.analyzer.plot_statistics()

#         return simulation_results

#     def simulate_day(self):
#         """
#         Simulate a single day of interactions, ordered by time intervals.

#         :return: A summary of interactions for the day.
#         """
#         daily_interactions = {
#             "6-8am": self._simulate_morning(),
#             "8am-5pm": self._simulate_daytime(),
#             "5-8pm": self._simulate_evening(),
#             "8pm-6am": self._simulate_night()
#         }

#         # Propagate disease based on interactions
#         self.disease_model.propagate(daily_interactions)

#         return daily_interactions

#     def _simulate_morning(self):
#         """
#         Simulate interactions in the morning (6-8am): Home and transport.

#         :return: A list of interactions for the morning.
#         """
#         interactions = []
#         interactions.extend(self._simulate_cluster_interactions(self.clusters["home"]))
#         interactions.extend(self.transport.simulate_transport())
#         return interactions

#     def _simulate_daytime(self):
#         """
#         Simulate interactions during the day (8am-5pm): Work and school.

#         :return: A list of interactions for the daytime.
#         """
#         interactions = []
#         interactions.extend(self._simulate_cluster_interactions(self.clusters["work"]))
#         interactions.extend(self._simulate_cluster_interactions(self.clusters["school"]))
#         return interactions

#     def _simulate_evening(self):
#         """
#         Simulate interactions in the evening (5-8pm): Transport and shopping.

#         :return: A list of interactions for the evening.
#         """
#         interactions = []
#         interactions.extend(self.transport.simulate_transport())
#         interactions.extend(self._simulate_cluster_interactions(self.clusters["shopping"]))
#         return interactions

#     def _simulate_night(self):
#         """
#         Simulate interactions at night (8pm-6am): Home only.

#         :return: A list of interactions for the night.
#         """
#         return self._simulate_cluster_interactions(self.clusters["home"])

#     def _simulate_cluster_interactions(self, cluster_list):
#         """
#         Simulate interactions within a list of clusters and their subclusters.

#         :param cluster_list: List of clusters to simulate.
#         :return: List of interactions within the clusters and subclusters.
#         """
#         interactions = []
#         for cluster in cluster_list:
#             subcluster_interactions = cluster.simulate_interactions()
#             interactions.extend(subcluster_interactions)
#         return interactions

#     def _apply_policies(self):
#         """
#         Apply health policies to modify agent behavior or cluster interactions.
#         """
#         for policy in self.policies:
#             policy.enforce(self.agents, self.clusters)

# # Example configuration for the clusters and transport
# example_config = {
#     "home": {"duration_mean": 480, "duration_std": 120},
#     "work": {"duration_mean": 480, "duration_std": 120, "min_links": 2},
#     "school": {"duration_mean": 300, "duration_std": 60},
#     "shopping": {"duration_mean": 37, "duration_std": 10, "max_agents": 50},
#     "transport": {"interval": 5, "duration_mean": 15, "duration_std": 5},
#     "household_sizes": [1, 2, 3, 4, 5, 6],
#     "household_distribution": [0.1, 0.2, 0.3, 0.2, 0.15, 0.05],
#     "work_sizes": [5, 10, 20, 50],
#     "work_distribution": [0.4, 0.3, 0.2, 0.1],
#     "school_sizes": [20, 30, 40],
#     "school_distribution": [0.5, 0.3, 0.2],
#     "shopping_centers": 5
# }

# # if __name__ == "__main__":
# #     from clusters import TransportInteraction
# #     from disease import DiseaseModel
# #     from policies import LockdownPolicy, SocialDistancingPolicy

# #     # Example agents
# #     agents = [f"Agent_{i}" for i in range(200)]

# #     # Create city cluster generator
# #     cluster_generator = CityClusterGenerator(example_config)

# #     # Transport interactions
# #     transport_interaction = TransportInteraction(agents, example_config["transport"])

# #     # Disease model
# #     disease_model = DiseaseModel()

# #     # Active policies
# #     policies = [LockdownPolicy(), SocialDistancingPolicy()]

# #     # Healthcare system
# #     municipalities = {
# #         "Municipio1": {"num_consultorios": 10, "num_policlinicos": 3, "num_hospitals": 1},
# #         "Municipio2": {"num_consultorios": 8, "num_policlinicos": 2, "num_hospitals": 1},
# #     }
# #     recovery_rates = {"consultorio": 0.8, "policlinico": 0.6, "hospital": 0.4}
# #     mortality_rates = {"consultorio": 0.1, "policlinico": 0.3, "hospital": 0.5}
# #     healthcare_system = HealthcareSystem(municipalities, recovery_rates, mortality_rates)

# #     # Simulation analyzer
# #     analyzer = SimulationAnalyzer()

# #     # Daily simulation
# #     simulation = DailySimulation(agents, cluster_generator, transport_interaction, example_config, disease_model, policies, healthcare_system, analyzer)
# #     simulation_results = simulation.simulate(days=10)
# #     print("Simulation Results Summary:", simulation_results)
