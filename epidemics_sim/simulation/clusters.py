import random
import networkx as nx

class Subcluster:
    def __init__(self, agents, topology="scale_free", interaction_probability=0.7):
        """
        Initialize a subcluster.

        :param agents: List of agents assigned to the subcluster.
        :param topology: Topology of the graph (e.g., "scale_free", "complete").
        :param interaction_probability: Probability that an edge results in an actual interaction.
        """
        self.agents = agents
        self.topology = topology
        self.interaction_probability = interaction_probability

    def generate_graph(self):
        """
        Generate a graph for the subcluster based on its topology.

        :return: A NetworkX graph representing the subcluster.
        """
        num_agents = len(self.agents)
        
        if num_agents < 2:
            return nx.Graph()

        if self.topology == "scale_free":
            m = max(1, min(2, num_agents - 1))  # Ensure m is within valid range
            graph = nx.barabasi_albert_graph(num_agents, m)
        elif self.topology == "complete":
            graph = nx.complete_graph(num_agents)
        else:
            raise ValueError(f"Unknown topology: {self.topology}")

        for i, agent in enumerate(self.agents):
            graph.nodes[i]["agent"] = agent

        return graph

    def simulate_interactions(self):
        """
        Simulate interactions for the subcluster during a specific time period.

        :return: List of interactions within the subcluster.
        """
        graph = self.generate_graph()
        interactions = []

        for edge in graph.edges:
            if random.random() < self.interaction_probability:  # Introduce randomness in interactions
                agent1 = graph.nodes[edge[0]]['agent']
                agent2 = graph.nodes[edge[1]]['agent']
                interactions.append((agent1, agent2))

        return interactions

class ClusterWithSubclusters:
    def __init__(self, subclusters, cluster_type, active_periods):
        """
        Initialize a cluster with pre-defined subclusters.

        :param subclusters: List of Subcluster instances.
        :param cluster_type: Type of cluster (e.g., "home", "work", "school", "shopping").
        :param active_periods: Time periods when the cluster is active.
        """
        self.subclusters = subclusters
        self.cluster_type = cluster_type
        self.active_periods = active_periods
        self.lockdown_is_active = False

    def enforce_lockdown(self):
        self.lockdown_is_active = True
    
    def remove_lockdown(self):
        self.lockdown_is_active = False

    def simulate_interactions(self, time_period):
        """
        Simulate interactions for all subclusters within this cluster during a specific time period.
        """
        interactions = []
        if not self.lockdown_is_active and time_period in self.active_periods:
            for subcluster in self.subclusters:
                interactions.extend(subcluster.simulate_interactions())
        return interactions
class CityClusterGenerator:
    def __init__(self, municipal_data):
        """
        Initialize the city cluster generator.

        :param municipal_data: Dictionary with municipal-specific data.
        """
        self.municipal_data = municipal_data

    def generate_clusters(self, agents):
        """
        Generate all types of clusters (home, work, school, shopping).

        :param agents: List of agents to assign to clusters.
        :return: Dictionary containing all generated clusters.
        """
        return {
            "work": self.generate_work_clusters(agents),
            "school": self.generate_school_clusters(agents),
            "shopping": self.generate_shopping_clusters(agents),
            "home": self.generate_home_clusters(agents),
        }

    def _get_agents_by_municipio(self, agents, municipio):
        """
        Filter agents belonging to a specific municipio.

        :param agents: List of agents.
        :param municipio: Name of the municipio.
        :return: List of agents belonging to the municipio.
        """
        return [agent for agent in agents if agent.municipio == municipio]

    def generate_home_clusters(self, agents): #TODO: Mejorar esto el tema de los adultos
        """
        Generate home clusters, where each subcluster represents a household.
        Se agrupan los agentes por municipio y se extraen hogares de tamaño aleatorio
        según la distribución configurada. Se asegura que cada hogar tenga al menos un adulto;
        si no es posible, se rompe el ciclo para ese municipio para evitar un bucle infinito.

        :param agents: List of agents to assign to home clusters.
        :return: A ClusterWithSubclusters instance for home.
        """
        home_subclusters = []

        for municipio, data in self.municipal_data.items():
            municipio_agents = self._get_agents_by_municipio(agents, municipio)
            household_sizes = list(data["hogares_por_tamano"].keys())
            household_distribution = list(data["hogares_por_tamano"].values())

            unassigned_agents = municipio_agents.copy()
            iteration = 0
            while unassigned_agents:
                iteration += 1
                # Seleccionar el tamaño del hogar según la distribución
                size_key = random.choices(household_sizes, household_distribution)[0]
                size_mapping = {
                    "1_persona": 1,
                    "2_personas": 2,
                    "3_personas": 3,
                    "4_personas": 4,
                    "5_personas_o_mas": random.randint(5, 8)
                }
                size = size_mapping[size_key]
                size = min(size, len(unassigned_agents))

                # Extraer el grupo de agentes para el hogar
                household_agents = unassigned_agents[:size]
                unassigned_agents = unassigned_agents[size:]

                # Verificar que el hogar tenga al menos un adulto
                if not any(agent.age >= 18 for agent in household_agents):
                    adults = [agent for agent in unassigned_agents if agent.age >= 18]
                    if adults:
                        adult = adults[0]
                        household_agents[-1] = adult
                        unassigned_agents.remove(adult)
                        print(f"Se asignó un adulto en municipio {municipio} en iteración {iteration}.")
                    else:
                        print(f"Advertencia: No hay suficientes adultos en {municipio} para completar el hogar.")
                        # Romper el ciclo para este municipio para evitar un bucle infinito
                        break

                home_subclusters.append(
                    Subcluster(household_agents, topology="complete")
                )

                # Verificar que la lista se esté reduciendo
                # if iteration > 10000:
                #     print(f"Advertencia: Demasiadas iteraciones en {municipio}. Posible bucle infinito.")
                #     break

            print(f"Finalizado la generación de hogares para {municipio}: {len(home_subclusters)} hogares generados.")

        return ClusterWithSubclusters(home_subclusters, cluster_type="home", active_periods= ["morning", "night"])


    def generate_work_clusters(self, agents): # TODO: Arreglar esto
        """
        Generate work clusters, where each subcluster represents a workplace.

        :param agents: List of agents to assign to work clusters.
        :return: A ClusterWithSubclusters instance for work.
        """
        work_subclusters = []

        for municipio, data in self.municipal_data.items():
            municipio_agents = [agent for agent in self._get_agents_by_municipio(agents, municipio) if 18 <= agent.age <= 64]
            work_sizes = list(data["distribucion_centros_laborales"].keys())
            work_distribution = list(data["distribucion_centros_laborales"].values())

            unassigned_agents = municipio_agents.copy()
            size_mapping = {"pequenos": 10, "medianos": 50, "grandes": 100}

            while unassigned_agents:
                size_key = random.choices(work_sizes, work_distribution)[0]
                size = size_mapping[size_key]
                size = min(size, len(unassigned_agents))

                workplace_agents = unassigned_agents[:size]
                unassigned_agents = unassigned_agents[size:]

                work_subclusters.append(Subcluster(workplace_agents, topology="scale_free"))

        return ClusterWithSubclusters(work_subclusters, "work",["daytime"])

    def generate_school_clusters(self, agents): # Ver de verdad cuantos hay
        """
        Generate school clusters, where each subcluster represents a school.

        :param agents: List of agents to assign to school clusters.
        :return: A ClusterWithSubclusters instance for schools.
        """
        school_subclusters = []

        for municipio, data in self.municipal_data.items():
            municipio_agents = [agent for agent in self._get_agents_by_municipio(agents, municipio) if 5 <= agent.age <= 22]
            school_levels = list(data["distribucion_estudiantes"].keys())
            school_distribution = list(data["distribucion_estudiantes"].values())

            size_mapping = {
                "primaria": 30,
                "secundaria": 40,
                "preuniversitario": 50,
                "universitario": 60
            }

            unassigned_agents = municipio_agents.copy()

            while unassigned_agents:
                level_key = random.choices(school_levels, school_distribution)[0]
                size = size_mapping[level_key]
                size = min(size, len(unassigned_agents))

                school_agents = unassigned_agents[:size]
                unassigned_agents = unassigned_agents[size:]

                school_subclusters.append(Subcluster(school_agents, topology="scale_free"))

        return ClusterWithSubclusters(school_subclusters, "school",["daytime"])

    def generate_shopping_clusters(self, agents):
        """
        Generate shopping clusters, where each subcluster represents a shopping center.

        :param agents: List of agents to assign to shopping clusters.
        :return: A ClusterWithSubclusters instance for shopping.
        """
        shopping_subclusters = []

        for municipio, data in self.municipal_data.items():
            municipio_agents = self._get_agents_by_municipio(agents, municipio)
            shopping_centers = data.get("shopping_centers", 5)

            # Select one agent per household to represent shoppers
            household_representatives = {}
            for agent in municipio_agents:
                if agent.household_id not in household_representatives:
                    household_representatives[agent.household_id] = agent

            shopping_agents = list(household_representatives.values())

            unassigned_agents = shopping_agents.copy()

            for _ in range(shopping_centers):
                if not unassigned_agents:
                    break
                size = random.randint(20, 50)  # Random cluster size for shopping centers
                size = min(size, len(unassigned_agents))

                shopping_center_agents = unassigned_agents[:size]
                unassigned_agents = unassigned_agents[size:]

                shopping_subclusters.append(Subcluster(shopping_center_agents, topology="scale_free"))

        return ClusterWithSubclusters(shopping_subclusters, "shopping",["evening"])
