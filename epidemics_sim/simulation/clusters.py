import random
import networkx as nx

class Subcluster:
    def __init__(self, agents, active_periods, topology="scale_free"):
        """
        Initialize a subcluster.

        :param agents: List of agents assigned to the subcluster.
        :param active_periods: List of periods during which the subcluster is active (e.g., ["morning", "daytime"]).
        :param topology: Topology of the graph (e.g., "scale_free", "complete").
        """
        self.agents = agents
        self.active_periods = active_periods
        self.topology = topology

    def generate_graph(self):
        """
        Generate a graph for the subcluster based on its topology.

        :return: A NetworkX graph representing the subcluster.
        """
        num_agents = len(self.agents)

        if num_agents < 2:
            # Return an empty graph for subclusters with fewer than 2 agents
            return nx.Graph()

        if self.topology == "scale_free":
            # Adjust m dynamically to ensure it satisfies NetworkX requirements
            m = min(2, num_agents - 1)
            graph = nx.barabasi_albert_graph(num_agents, m)
        elif self.topology == "complete":
            graph = nx.complete_graph(num_agents)
        else:
            raise ValueError(f"Unknown topology: {self.topology}")

        # Assign agents to graph nodes
        for i, agent in enumerate(self.agents):
            graph.nodes[i]["agent"] = agent

        return graph

    def simulate_interactions(self, time_period):
        """
        Simulate interactions for the subcluster during a specific time period.

        :param time_period: The time period (e.g., "morning", "daytime", "evening", "night").
        :return: List of interactions within the subcluster.
        """
        if time_period not in self.active_periods:
            return []

        graph = self.generate_graph()
        interactions = []

        for edge in graph.edges:
            agent1 = graph.nodes[edge[0]]['agent']
            agent2 = graph.nodes[edge[1]]['agent']
            interactions.append((agent1, agent2))

        return interactions

class ClusterWithSubclusters:
    def __init__(self, subclusters, cluster_type):
        """
        Initialize a cluster with pre-defined subclusters.

        :param subclusters: List of Subcluster instances.
        :param cluster_type: Type of cluster (e.g., "home", "work", "school", "shopping").
        """
        self.subclusters = subclusters
        self.cluster_type = cluster_type

    def simulate_interactions(self, time_period):
        """
        Simulate interactions for all subclusters within this cluster during a specific time period.

        :param time_period: The time period (e.g., "morning", "daytime", "evening", "night").
        :return: List of interactions within all subclusters.
        """
        interactions = []
        for subcluster in self.subclusters:
            interactions.extend(subcluster.simulate_interactions(time_period))
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
            "home": self.generate_home_clusters(agents),
            "work": self.generate_work_clusters(agents),
            "school": self.generate_school_clusters(agents),
            "shopping": self.generate_shopping_clusters(agents),
        }

    def _get_agents_by_municipio(self, agents, municipio):
        """
        Filter agents belonging to a specific municipio.

        :param agents: List of agents.
        :param municipio: Name of the municipio.
        :return: List of agents belonging to the municipio.
        """
        return [agent for agent in agents if agent.municipio == municipio]

    def generate_home_clusters(self, agents):
        """
        Generate home clusters, where each subcluster represents a household.

        :param agents: List of agents to assign to home clusters.
        :return: A ClusterWithSubclusters instance for home.
        """
        home_subclusters = []

        for municipio, data in self.municipal_data.items():
            municipio_agents = self._get_agents_by_municipio(agents, municipio)
            household_sizes = list(data["hogares_por_tamano"].keys())
            household_distribution = list(data["hogares_por_tamano"].values())

            unassigned_agents = municipio_agents.copy()

            while unassigned_agents:
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

                household_agents = unassigned_agents[:size]
                unassigned_agents = unassigned_agents[size:]

                # Ensure at least one adult in the household
                if not any(agent.age >= 18 for agent in household_agents):
                    adults = [agent for agent in unassigned_agents if agent.age >= 18]
                    if adults:
                        adult = adults.pop(0)
                        household_agents[-1] = adult
                        unassigned_agents.remove(adult)

                home_subclusters.append(Subcluster(household_agents, ["morning", "evening", "night"], topology="complete"))

        return ClusterWithSubclusters(home_subclusters, "home")

    def generate_work_clusters(self, agents):
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

                work_subclusters.append(Subcluster(workplace_agents, ["daytime"], topology="scale_free"))

        return ClusterWithSubclusters(work_subclusters, "work")

    def generate_school_clusters(self, agents):
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

                school_subclusters.append(Subcluster(school_agents, ["morning", "daytime"], topology="scale_free"))

        return ClusterWithSubclusters(school_subclusters, "school")

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

                shopping_subclusters.append(Subcluster(shopping_center_agents, ["evening"], topology="scale_free"))

        return ClusterWithSubclusters(shopping_subclusters, "shopping")
