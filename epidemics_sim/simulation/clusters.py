import random
import networkx as nx
from epidemics_sim.agents.base_agent import State

class Subcluster:
    def __init__(self, agents, topology="scale_free", interaction_probability=0.7):
        self.agents = agents
        self.topology = topology
        self.interaction_probability = interaction_probability

    def generate_graph(self):
        num_agents = len(self.agents)
        if num_agents < 2:
            return nx.Graph()

        if self.topology == "scale_free":
            m = max(1, min(2, num_agents - 1))
            graph = nx.barabasi_albert_graph(num_agents, m)
        elif self.topology == "complete":
            graph = nx.complete_graph(num_agents)
        else:
            raise ValueError(f"Unknown topology: {self.topology}")

        for i, agent in enumerate(self.agents):
            graph.nodes[i]["agent"] = agent

        return graph

    # def update_agents(self, new_agents):
    #     """
    #     Remove deceased agents from the subcluster and update the graph and matrix.
    #     """
    #     self.agents = new_agents

    def simulate_interactions(self):
        graph = self.generate_graph()
        interactions = []
        for edge in graph.edges:
            if random.random() < self.interaction_probability:
                agent1 = graph.nodes[edge[0]]['agent']
                agent2 = graph.nodes[edge[1]]['agent']
                # if agent1.is_hospitalized or agent1.is_isolated or agent2.is_hospitalized or agent2.is_isolated:
                #     continue  # Skip agents who shouldn't interact
                interactions.append((agent1, agent2))
        return interactions

class ClusterWithSubclusters:
    def __init__(self, subclusters, cluster_type, active_periods):
        self.subclusters = subclusters
        self.cluster_type = cluster_type
        self.active_periods = active_periods
        self.lockdown_is_active = False

    def enforce_lockdown(self):
        self.lockdown_is_active = True
    
    def remove_lockdown(self):
        self.lockdown_is_active = False

    def simulate_interactions(self, time_period):
        interactions = []
        if not self.lockdown_is_active and time_period in self.active_periods:
            for subcluster in self.subclusters:
                interactions.extend(subcluster.simulate_interactions())
        return interactions

class CityClusterGenerator:
    def __init__(self, municipal_data):
        self.total_companies = municipal_data["total_empresas"]
        self.municipal_data = municipal_data["municipios"]
    
    def generate_clusters(self, agents):
        return {
            "work": self.generate_work_clusters(agents),
            "school": self.generate_school_clusters(agents),
            "shopping": self.generate_shopping_clusters(agents),
            "home": self.generate_home_clusters(agents),
        }
    def generate_home_clusters(self, agents):
        home_subclusters = []
        for municipio, data in self.municipal_data.items():
            municipio_agents = [agent for agent in agents if agent.municipio == municipio]
            total_population = len(municipio_agents)
            avg_household_size = float(data["Promedio de Personas por Unidad de Alojamiento"])

            # Determinar la cantidad de hogares a partir del promedio
            estimated_households = max(1, round(total_population / avg_household_size))

            random.shuffle(municipio_agents)
            unassigned_agents = municipio_agents.copy()

            for _ in range(estimated_households):
                if not unassigned_agents:
                    break
                size = max(1, round(random.gauss(avg_household_size, 1)))  # Distribución normal alrededor del promedio
                size = min(size, len(unassigned_agents))  

                household_agents = unassigned_agents[:size]
                unassigned_agents = unassigned_agents[size:]

                # Asegurar que al menos haya un adulto en el hogar
                if not any(agent.age >= 18 for agent in household_agents):
                    adults = [a for a in unassigned_agents if a.age >= 18]
                    if adults:
                        household_agents[-1] = adults.pop(0)
                        unassigned_agents.remove(household_agents[-1])

                home_subclusters.append(Subcluster(household_agents, topology="complete"))

        return ClusterWithSubclusters(home_subclusters, "home", ["morning", "night"])


    def generate_work_clusters(self, agents):
        work_subclusters = []
        workers = [agent for agent in agents if 18 <= agent.age <= 64]
        random.shuffle(workers)

        min_size, max_size = 5, 50  # Tamaño mínimo y máximo de cada empresa
        company_sizes = [random.randint(min_size, max_size) for _ in range(self.total_companies)]
        unassigned_agents = workers.copy()

        for size in company_sizes:
            if not unassigned_agents:
                break
            size = min(size, len(unassigned_agents))
            work_agents = unassigned_agents[:size]
            unassigned_agents = unassigned_agents[size:]
            work_subclusters.append(Subcluster(work_agents, topology="scale_free"))
        
        return ClusterWithSubclusters(work_subclusters, "work", ["daytime"])
    
    def generate_school_clusters(self, agents):
        school_subclusters = []
        for municipio, data in self.municipal_data.items():
            if "Escuelas" not in data:
                continue
            school_types = data["Escuelas"]
            for school_type, num_schools in school_types.items():
                students = [agent for agent in agents if agent.municipio == municipio and agent.occupation == "student"]
                random.shuffle(students)
                school_sizes = [random.randint(20, 50) for _ in range(int(num_schools))]
                unassigned_students = students.copy()
                for size in school_sizes:
                    if not unassigned_students:
                        break
                    size = min(size, len(unassigned_students))
                    school_agents = unassigned_students[:size]
                    unassigned_students = unassigned_students[size:]
                    school_subclusters.append(Subcluster(school_agents, topology="scale_free"))
        return ClusterWithSubclusters(school_subclusters, "school", ["daytime"])
    
    def generate_shopping_clusters(self, agents):
        shopping_subclusters = []
        household_representatives = {}
        for agent in agents:
            if agent.household_id not in household_representatives and agent.age >= 18:
                household_representatives[agent.household_id] = agent
        shoppers = list(household_representatives.values())
        random.shuffle(shoppers)
        num_shopping_centers = max(10, len(shoppers) // 50)
        shopping_sizes = [random.randint(20, 50) for _ in range(num_shopping_centers)]
        unassigned_shoppers = shoppers.copy()
        for size in shopping_sizes:
            if not unassigned_shoppers:
                break
            size = min(size, len(unassigned_shoppers))
            shopping_agents = unassigned_shoppers[:size]
            unassigned_shoppers = unassigned_shoppers[size:]
            shopping_subclusters.append(Subcluster(shopping_agents, topology="scale_free"))
        return ClusterWithSubclusters(shopping_subclusters, "shopping", ["evening"])

    def generate_school_clusters(self, agents):
        school_subclusters = []
        school_age_mapping = {
            "Circulos infantiles": (0, 5),
            "Primaria": (6, 11),
            "Secundaria basica": (12, 14),
            "Preuniversitario": (15, 17),
            "Tecnica y profesional": (18, 22)
        }

        for municipio, data in self.municipal_data.items():
            if "Escuelas" not in data:
                continue
            
            for school_type, num_schools in data["Escuelas"].items():
                if school_type not in school_age_mapping:
                    continue
                age_range = school_age_mapping[school_type]
                students = [agent for agent in agents if agent.municipio == municipio and age_range[0] <= agent.age <= age_range[1]]
                random.shuffle(students)

                school_sizes = [random.randint(20, 50) for _ in range(int(num_schools))]
                unassigned_students = students.copy()

                for size in school_sizes:
                    if not unassigned_students:
                        break
                    size = min(size, len(unassigned_students))
                    school_agents = unassigned_students[:size]
                    unassigned_students = unassigned_students[size:]
                    school_subclusters.append(Subcluster(school_agents, topology="scale_free"))

        return ClusterWithSubclusters(school_subclusters, "school", ["daytime"])