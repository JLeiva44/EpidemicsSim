import random
import networkx as nx
from epidemics_sim.agents.base_agent import State

class Subcluster:
    def __init__(self, agents,cluster, topology="scale_free"):
        """
        Inicializa un subcluster con un grafo estático y probabilidad de interacción ajustable.
        
        :param agents: Lista de agentes en el subcluster.
        :param topology: Topología del grafo ("scale_free" o "complete").
        :param interaction_probability: Probabilidad de que una conexión en el grafo genere una interacción.
        """
        self.agents = agents
        self.topology = topology
        self.cluster = cluster
        self.graph = self.generate_graph()  # Se genera una vez y no se vuelve a calcular en cada paso

    def generate_graph(self):
        """
        Genera un grafo basado en la topología especificada.
        """
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

    def remove_agent(self, agent):
        """
        Elimina un agente del grafo cuando fallece para evitar futuras interacciones.
        """
        for node in list(self.graph.nodes):
            if self.graph.nodes[node]["agent"] == agent:
                self.graph.remove_node(node)
                break

    def simulate_interactions(self):
        """
        Simula interacciones dentro del subcluster basándose en la probabilidad de interacción.
        """
        interactions = []
        for edge in list(self.graph.edges):
            agent1 = self.graph.nodes[edge[0]]['agent']
            agent2 = self.graph.nodes[edge[1]]['agent']
            
            # Evitar interacciones con agentes fallecidos
            if self.cluster.cluster_type == "shopping":
                if agent1.infection_status['state'] == State.DECEASED or agent1.is_hospitalized or agent1.is_isolated:
                    self.update_shopping_agents(agent1)
                elif agent2.infection_status['state'] == State.DECEASED or agent2.is_hospitalized or agent2.is_isolated:
                    self.update_shopping_agents(agent2)
                continue    
            if agent1.infection_status["state"] == State.DECEASED or agent2.infection_status["state"] == State.DECEASED:
                continue

            if agent1.is_hospitalized or agent2.is_hospitalized or agent1.is_isolated or agent2.is_isolated:
                continue

            if random.random() < self.cluster.interaction_probability:
                interactions.append((agent1, agent2))
        
        return interactions
    
    def adjust_interaction_probability(self, new_probability):
        """
        Permite ajustar la probabilidad de interacción sin modificar la estructura del grafo.
        """
        self.interaction_probability = new_probability

    def update_shopping_agents(self, agent):
        """
        Actualiza la lista de compradores si un agente fallece, está hospitalizado o aislado.
        """
        household_id = agent.household_id
        household_members = [member for member in agent.hosehold if member.agent_id != agent.agent_id]
        best_candidate = None
        best_age = -1  # Almacena la mejor edad encontrada

        # Buscar el mejor representante en una sola iteración
        for member in household_members:
            if member.infection_status["state"] == State.DECEASED or member.is_hospitalized or member.is_isolated:
                continue  # Saltar agentes no disponibles

            if member.age >= 18:
                best_candidate = member  # Adulto disponible, mejor opción
                break  # No es necesario seguir buscando

            if member.age > best_age:  # Guardar el mejor candidato si no es adulto
                best_candidate = member
                best_age = member.age

        # Remover el agente del grafo
        for node in list(self.graph.nodes):
            if self.graph.nodes[node]["agent"] == agent:
                self.graph.remove_node(node)
                break

        # Si se encontró un nuevo representante, actualizar el cluster
        if best_candidate and best_age >= 12:
            self.agents.append(best_candidate)  # Agregar al nuevo representante
            self.graph = self.generate_graph()  # Regenerar el grafo con el nuevo agente
            # new_node = len(self.graph.nodes)  # Nuevo índice de nodo en el grafo
            # self.graph.add_node(new_node, agent=best_candidate)

            # Conectar con vecinos existentes en la red de compras
            # for neighbor in self.graph.nodes:
            #     if random.random() < 0.5:  # Probabilidad arbitraria de reconectar
            #         self.graph.add_edge(new_node, neighbor)



class ClusterWithSubclusters:
    def __init__(self, subclusters, cluster_type, active_periods ,interaction_probability):
        """
        Agrupa varios subclusters dentro de un tipo de cluster (hogares, trabajo, etc.).
        """
        self.subclusters = subclusters
        self.cluster_type = cluster_type
        self.active_periods = active_periods
        self.lockdown_is_active = False
        self.interaction_probability = interaction_probability

    def enforce_lockdown(self):
        self.lockdown_is_active = True
    
    def remove_lockdown(self):
        self.lockdown_is_active = False

    def simulate_interactions(self, time_period):
        """
        Simula interacciones en todos los subclusters durante un período activo.
        """
        interactions = []
        if not self.lockdown_is_active and time_period in self.active_periods:
            for subcluster in self.subclusters:
                interactions.extend(subcluster.simulate_interactions())
        return interactions
    
    def adjust_interaction_probability(self, new_probability):
        """
        Permite ajustar la probabilidad de interacción sin modificar la estructura del grafo.
        """
        self.interaction_probability = new_probability
        
    # def adjust_cluster_interactions(self, new_probability):
    #     """
    #     Ajusta la probabilidad de interacción en todos los subclusters de este cluster.
    #     """
    #     for subcluster in self.subclusters:
    #         subcluster.adjust_interaction_probability(new_probability)

    def remove_deceased_agents(self, deceased_agents):
        """
        Elimina agentes fallecidos de todos los subclusters del cluster.
        """
        for subcluster in self.subclusters:
            for agent in deceased_agents:
                subcluster.remove_agent(agent)

class CityClusterGenerator:
    def __init__(self, municipal_data):
        self.total_companies = municipal_data["total_empresas"]
        self.total_stores = municipal_data["total_tiendas"]
        self.municipal_data = municipal_data["municipios"]
    
    def generate_clusters(self, agents):
        return {
            "home": self.generate_home_clusters(agents),
            "school": self.generate_school_clusters(agents),
            "work": self.generate_work_clusters(agents),
            "shopping": self.generate_shopping_clusters(agents),
        }
    
    def generate_home_clusters(self, agents): # TODO mejorar la asinacion de hogares para no tener que apsar de nuevo
        home_subclusters = []
        household_id_counter = 0  # 🔹 Contador único para asignar household_id
        cluster = ClusterWithSubclusters(home_subclusters, "home", ["morning", "night"],interaction_probability=random.uniform(0.8, 1.0))

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

                # 🔹 Asignar un household_id único a todos los agentes en este hogar
                for agent in household_agents:
                    agent.household_id = household_id_counter
                    agent.household = household_agents
                household_id_counter += 1  # Incrementar para el siguiente hogar

                home_subclusters.append(Subcluster(household_agents,cluster, topology="complete"))

        cluster.subclusters = home_subclusters
        print("Home clusters generated")
        return cluster


    def generate_work_clusters(self, agents):
        work_subclusters = []
        cluster = ClusterWithSubclusters(work_subclusters, "work", ["daytime"],interaction_probability=random.uniform(0.3,0.6))
        workers = [agent for agent in agents if agent.occupation == "worker"]
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
            work_subclusters.append(Subcluster(work_agents,cluster, topology="scale_free"))
        
        cluster.subclusters = work_subclusters
        print("Work clusters generated")
        return cluster
    
    
    def generate_shopping_clusters(self, agents):
        shopping_subclusters = []
        cluster = ClusterWithSubclusters(shopping_subclusters, "shopping", ["evening"],interaction_probability=random.uniform(0.1, 0.4))
        household_representatives = {}

        # ✅ Seleccionar un representante mayor de 18 años por hogar
        for agent in agents:  
            if agent.household_id not in household_representatives and agent.age >= 18:
                household_representatives[agent.household_id] = agent

        shoppers = list(household_representatives.values())
        random.shuffle(shoppers)

        # ✅ Usar self.total_stores como número fijo de tiendas
        num_shopping_centers = min(self.total_stores, max(1, len(shoppers) // 50))

        if num_shopping_centers == 0:
            return ClusterWithSubclusters([], "shopping", ["evening"])  # Evitar errores si no hay shoppers

        # ✅ Distribuir compradores en las tiendas
        shopping_sizes = [random.randint(15, 40) for _ in range(num_shopping_centers)]  
        unassigned_shoppers = shoppers.copy()

        for size in shopping_sizes:
            if not unassigned_shoppers:
                break
            size = min(size, len(unassigned_shoppers))
            shopping_agents = unassigned_shoppers[:size]
            unassigned_shoppers = unassigned_shoppers[size:]
            shopping_subclusters.append(Subcluster(shopping_agents,cluster, topology="scale_free"))

        cluster.subclusters = shopping_subclusters
        print("Shopping clusters generated")
        return cluster


    def generate_school_clusters(self, agents):
        school_subclusters = []
        cluster = ClusterWithSubclusters(school_subclusters, "school", ["daytime"], interaction_probability= random.uniform(0.5,0.9))
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

                students = [agent for agent in agents if agent.municipio == municipio and agent.occupation == "student" and age_range[0] <= agent.age <= age_range[1]]
                random.shuffle(students)

                school_sizes = [random.randint(20, 50) for _ in range(int(num_schools))]
                unassigned_students = students.copy()

                for size in school_sizes:
                    if not unassigned_students:
                        break
                    size = min(size, len(unassigned_students))
                    school_agents = unassigned_students[:size]
                    unassigned_students = unassigned_students[size:]
                    school_subclusters.append(Subcluster(school_agents,cluster, topology="scale_free"))

        cluster.subclusters = school_subclusters
        print("School clusters generated")
        return cluster