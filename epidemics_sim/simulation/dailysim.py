import random
from epidemics_sim.simulation.clusters import CityClusterGenerator
from epidemics_sim.simulation.healthcare import HealthcareSystem
from epidemics_sim.simulation.simulation_utils import SimulationAnalyzer
from epidemics_sim.agents.base_agent import State

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
        self.disease_model.initialize_infections(infected_agents)

    def simulate(self, days, interval="daily"):
        """
        Simulate interactions over multiple days.

        :param days: Number of days to simulate.
        :param interval: Interval to aggregate statistics ('daily', 'weekly', 'monthly').
        :return: Summary of interactions and disease progression over the simulation period.
        """
        simulation_results = []

        for day in range(days):
            print(f"Simulating Day {day + 1}...")

            # Simular interacciones y propagación
            daily_summary = self.simulate_day()
            simulation_results.append(daily_summary)

            # 1️⃣ Progresar la infección para todos los agentes
            for agent in self.agents:
                self.disease_model.progress_infection(agent)

            # 2️⃣ 🔥 REGISTRAR ESTADÍSTICAS ANTES de eliminar agentes muertos
            self.analyzer.record_daily_stats(self.agents)

            # 3️⃣ 🏴 REMOVER AGENTES MUERTOS DESPUÉS de registrar estadísticas
            self.agents = [agent for agent in self.agents if agent.infection_status['state'] != State.DECEASED]

        # 4️⃣ GENERAR REPORTE FINAL 🔍
        report = self.analyzer.generate_report()
        
        # 5️⃣ 🔥 Mostrar estadísticas según el intervalo seleccionado
        if interval in ["daily", "weekly", "monthly"]:
            stats = self.analyzer.compute_temporal_stats(interval)
            print(f"\n📊 {interval.capitalize()} Stats: {stats}")

        # 6️⃣ 📊 Graficar la progresión de la enfermedad
        self.analyzer.plot_disease_progression()

        return report
    # def simulate(self, days):
    #     """
    #     Simulate interactions over multiple days.

    #     :param days: Number of days to simulate.
    #     :return: Summary of interactions and disease progression over the simulation period.
    #     """
    #     simulation_results = []

    #     for day in range(days):
    #         print(f"Simulating Day {day + 1}...")
    #         daily_summary = self.simulate_day()
    #         simulation_results.append(daily_summary)

    #         # Propagate and progress the infection for all agents
    #         for agent in self.agents:
    #             self.disease_model.progress_infection(agent)

    #         # Record daily statistics
    #         self.analyzer.record_daily_stats(self.agents)
            
    #         # Sacar a los agentes muertos 
    #         # # 2️⃣ ELIMINAR AGENTES MUERTOS 🔥
    #         self.agents = [agent for agent in self.agents if agent.infection_status['state'] != State.DECEASED]
   


    #     # Generate and plot the final report
    #     report = self.analyzer.generate_report()
    #     self.analyzer.plot_disease_progression()

    #     return report

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
        #interactions.extend(self.transport.simulate_transport("morning"))
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
        #interactions.extend(self.transport.simulate_transport("evening"))
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
