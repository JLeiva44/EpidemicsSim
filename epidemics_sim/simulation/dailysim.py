import random
from epidemics_sim.simulation.clusters import CityClusterGenerator
from epidemics_sim.agents.base_agent import State
from multiprocessing import Pool

class DailySimulation:
    def __init__(self, agents, cluster_generator, disease_model, policies, healthcare_system, initial_infected):
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
        
        self.disease_model = disease_model
        self.policies = policies
        self.healthcare_system = healthcare_system
        #self.analyzer = analyzer
        self.clusters = self.cluster_generator.generate_clusters(self.agents.values())

        # Initialize infections
        self._initialize_infections(initial_infected)

    def _initialize_infections(self, initial_infected):
        """
        Infect a specified number of agents at the start of the simulation.

        :param initial_infected: Number of agents to infect initially.
        """
        infected_agents = random.sample(list(self.agents.values()), initial_infected)
        self.disease_model.initialize_infections(infected_agents)


    def simulate(self, days):
        """
        Simulate interactions over multiple days.

        :param days: Number of days to simulate.
        :return: Summary of interactions and disease progression over the simulation period.
        """
        simulation_results = []
        week_counter = 0

        for day in range(days):
            if week_counter == 7 :
                week_counter = 0
            print(f"Simulating Day {day + 1}...")
            print("...")

            # 1️⃣ Simular interacciones y propagación
            daily_summary = self.simulate_day(day)
            
            simulation_results.append(daily_summary)

            # 2️⃣ Propagar enfermedad solo con los agentes activos
            self.disease_model.propagate(daily_summary)

            
            # 2️⃣ Progresar la infección en los agentes
            for agent in self.agents.values():
                if agent.infection_status['state'] == State.INFECTED:
                    self.disease_model.progress_infection(agent)

            

            # 3️⃣ Ejecutar las operaciones del sistema de salud
            self.healthcare_system.daily_operations(self.agents.values(), self.clusters,sum([len(interactions) for interactions in daily_summary.values()]), day)

            
            
            # 4️⃣ Eliminar agentes muertos después de registrar estadísticas
            deceased = [agent for agent in self.agents.values() if agent.infection_status["state"] == State.DECEASED]
            if len(deceased) > 0:
                self.agents = {agent_id: agent for agent_id, agent in self.agents.items() if agent.infection_status["state"] != State.DECEASED}

                # pOR AHORA SOLO LOS IGNORA, ASI OPTIMIZO EL CODIGO
                # for cluster in self.clusters.values(): # ver si se puede optimizar para que solamente los 
                #     cluster.remove_deceased_agents(deceased)

            week_counter +=1

        # 5️⃣ Generar reporte y gráficos
        self.healthcare_system.analyzer.generate_full_report()


    def simulate_day(self, day):
        """
        Simulate a single day of interactions, ordered by time intervals.

        :return: A summary of interactions for the day.
        """
        # TODO : Posible mejora (y pasar active_agents como parametro a los metodos)
        # active_agents = [
        # agent for agent in self.agents.values()
        # if not (agent.is_hospitalized or agent.is_isolated)
        # ]

        # with Pool() as pool:
        #     results = pool.starmap(self._simulate_period, [
        #         ("morning",),
        #         ("daytime",),
        #         ("evening",),
        #     ])
        # daily_interactions = dict(zip(["morning", "daytime", "evening"], results))
        daily_interactions = {
        "morning": self._simulate_morning(),
        "daytime": self._simulate_daytime(),
        "evening": self._simulate_evening() if day % 7 == 0 else [],
        }

       # 1️⃣ Excluir agentes hospitalizados o aislados
        #Lo voy a dejar para ver si estan llegando los hospitalizados aqui ya que los quite en los clusters
        # filtered_interactions = { #TODO : Ver si se puede mejorar esto de manera que no se tenga que sacar despues de hecho
        #     period: [(a1, a2) for a1, a2 in interactions
        #             if not (a1.is_hospitalized or a2.is_hospitalized or a1.is_isolated or a2.is_isolated)]
        #     for period, interactions in daily_interactions.items()
        # }

        
        return daily_interactions

    def _simulate_period(self, period, agents = None):
        """
        Simulate interactions for a specific period.
        """
        if period == "morning":
            return self._simulate_morning()
        elif period == "daytime":
            return self._simulate_daytime()
        elif period == "evening":
            return self._simulate_evening()
        elif period == "night":
            return self._simulate_night()
        
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

    # def _apply_policies(self):
    #     """
    #     Apply health policies to modify agent behavior or cluster interactions.
    #     """
    #     for policy in self.policies:
    #         policy.enforce(self.agents, self.clusters)
