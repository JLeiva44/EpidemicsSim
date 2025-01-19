import random
from epidemics_sim.simulation.clusters_whit_subclusters import ClusterWithSubclusters

class CityClusterGenerator:
    def __init__(self,municipal_data):
        """
        Initialize the city cluster generator.

        :param config: Configuration dictionary containing parameters for generating clusters.
        :param municipal_data: Dictionary with municipal-specific data (e.g., population distribution, cluster sizes).
        """
        self.municipal_data = municipal_data

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
        Generate home clusters based on household IDs assigned during population generation.

        :param agents: List of agents to assign to home clusters.
        :return: List of home clusters.
        """
        households = {}

        # Agrupar agentes por household_id
        for agent in agents:
            household_id = agent.household_id
            if household_id not in households:
                households[household_id] = []
            households[household_id].append(agent)

        # Crear un cluster por cada hogar
        home_clusters = [ClusterWithSubclusters(household, self.municipal_data, "home", "home") for household in households.values()]
        return home_clusters

    def generate_work_clusters(self, agents):
        """
        Generate work clusters with subclusters (e.g., companies) based on municipal-specific data and inter-municipal probabilities.

        :param agents: List of agents to assign to work clusters.
        :return: List of work clusters with subclusters.
        """
        clusters = []

        for municipio, data in self.municipal_data.items():
            municipio_agents = self._get_agents_by_municipio(agents, municipio)
            work_sizes = list(data["distribucion_centros_laborales"].keys())
            work_distribution = list(data["distribucion_centros_laborales"].values())

            unassigned_agents = municipio_agents.copy()
            while unassigned_agents:
                size_key = random.choices(work_sizes, work_distribution)[0]
                size_mapping = {"pequenos": 10, "medianos": 50, "grandes": 100}
                size = size_mapping[size_key]
                size = min(size, len(unassigned_agents))
                cluster_agents = unassigned_agents[:size]
                unassigned_agents = unassigned_agents[size:]

                clusters.append(ClusterWithSubclusters(cluster_agents, self.municipal_data, "work", "work"))

        return clusters

    def generate_school_clusters(self, agents):
        """
        Generate school clusters with subclusters (e.g., schools) based on municipal-specific data.

        :param agents: List of agents to assign to school clusters.
        :return: List of school clusters with subclusters.
        """
        clusters = []
        for municipio, data in self.municipal_data.items():
            municipio_agents = self._get_agents_by_municipio(agents, municipio)
            school_sizes = list(data["distribucion_estudiantes"].keys())
            school_distribution = list(data["distribucion_estudiantes"].values())

            unassigned_agents = municipio_agents.copy()
            while unassigned_agents:
                size_key = random.choices(school_sizes, school_distribution)[0]
                size_mapping = {"primaria": 30, "secundaria": 40, "preuniversitario": 50, "tecnico_profesional": 60}
                size = size_mapping[size_key]
                size = min(size, len(unassigned_agents))
                cluster_agents = unassigned_agents[:size]
                unassigned_agents = unassigned_agents[size:]

                clusters.append(ClusterWithSubclusters(cluster_agents, self.municipal_data, "school", "school"))

        return clusters

    def generate_shopping_clusters(self, agents):
        """
        Generate shopping clusters with subclusters (e.g., shopping centers).

        :param agents: List of agents to assign to shopping clusters.
        :return: List of shopping clusters with subclusters.
        """
        clusters = []
        for municipio, data in self.municipal_data.items():
            municipio_agents = self._get_agents_by_municipio(agents, municipio)
            shopping_centers = data.get("shopping_centers", 5)

            unassigned_agents = municipio_agents.copy()
            for _ in range(shopping_centers):
                if not unassigned_agents:
                    break
                size = random.randint(20, 50)  # Random cluster size for shopping
                size = min(size, len(unassigned_agents))
                cluster_agents = unassigned_agents[:size]
                unassigned_agents = unassigned_agents[size:]

                clusters.append(ClusterWithSubclusters(cluster_agents, self.municipal_data, "shopping", "shopping"))

        return clusters
