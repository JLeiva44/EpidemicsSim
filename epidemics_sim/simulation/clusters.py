import random
import networkx as nx
from epidemics_sim.agents.base_agent import State

class Subcluster:
    def __init__(self, agents, cluster, topology="scale_free"):
        self.agents = agents
        self.topology = topology
        self.cluster = cluster
        self.graph = self.generate_graph()

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

    def remove_agent(self, agent):
        for node in list(self.graph.nodes):
            if self.graph.nodes[node]["agent"] == agent:
                self.graph.remove_node(node)
                self.agents.remove(agent)
                break

    def simulate_interactions(self, agents):
        interactions = []
        to_update = []  # Lista para evitar múltiples regeneraciones del grafo

        for edge in list(self.graph.edges):
            agent1 = self.graph.nodes[edge[0]]['agent']
            agent2 = self.graph.nodes[edge[1]]['agent']
            
            # if self.cluster.cluster_type == "shopping":
            #     try:
            #         if (agents[agent1.agent_id].infection_status['state'] == State.DECEASED or 
            #             agents[agent1.agent_id].is_hospitalized or 
            #             agents[agent1.agent_id].is_isolated):
            #             to_update.append(agent1)
            #             continue
            #     except KeyError:
            #         # Si el agente no existe en el diccionario, se asume que está muerto
            #         continue

            #     try:
            #         if (agents[agent2.agent_id].infection_status['state'] == State.DECEASED or 
            #             agents[agent2.agent_id].is_hospitalized or 
            #             agents[agent2.agent_id].is_isolated):
            #             to_update.append(agent2)
            #             continue
            #     except KeyError:
            #         continue

            try:
                if (agents[agent1.agent_id].infection_status["state"] == State.DECEASED or 
                    agents[agent2.agent_id].infection_status["state"] == State.DECEASED):
                    continue
            except KeyError:
                continue

            # if self.cluster.cluster_type == "shopping":
            #     if agents[agent1.agent_id].infection_status['state'] == State.DECEASED or agents[agent1.agent_id].is_hospitalized or agents[agent1.agent_id].is_isolated:
            #         to_update.append(agent1)
            #         continue
            #     elif agents[agent2.agent_id].infection_status['state'] == State.DECEASED or agents[agent2.agent_id].is_hospitalized or agents[agent2.agent_id].is_isolated:
            #         to_update.append(agent2)
            #         continue    
            # if agents[agent1.agent_id].infection_status["state"] == State.DECEASED or agents[agent2.agent_id].infection_status["state"] == State.DECEASED:
            #     continue

            # if agents[agent1.agent_id].is_hospitalized or agents[agent2.agent_id].is_hospitalized or agents[agent1.agent_id].is_isolated or agents[agent2.agent_id].is_isolated:
            #     continue

            if random.random() < self.cluster.interaction_probability:
                interactions.append((agent1.agent_id, agent2.agent_id))
        
        for agent in to_update:
            self.update_shopping_agents(agent)
        
        return interactions
    
    def update_shopping_agents(self, agent):
        household_members = [member for member in agent.household if member.agent_id != agent.agent_id]
        best_candidate = None
        best_age = -1

        for member in household_members:
            if member.infection_status["state"] == State.DECEASED or member.is_hospitalized or member.is_isolated:
                continue
            if member.age >= 18:
                best_candidate = member
                break
            if member.age > best_age:
                best_candidate = member
                best_age = member.age

        self.remove_agent(agent)

        if best_candidate and best_age >= 12:
            self.agents.append(best_candidate)
            self.graph.add_node(len(self.graph.nodes), agent=best_candidate)

            for neighbor in list(self.graph.nodes):  # Convertimos a lista para evitar modificar el diccionario original
                if random.random() < 0.5:
                    self.graph.add_edge(len(self.graph.nodes) - 1, neighbor)
            # for neighbor in self.graph.nodes:
            #     if random.random() < 0.5:
            #         self.graph.add_edge(len(self.graph.nodes) - 1, neighbor)
        else:
            print(f"Advertencia: El hogar {agent.household_id} se ha quedado sin representante para comprar.")

# class Subcluster:
#     def __init__(self, agents,cluster, topology="scale_free"):
#         """
#         Inicializa un subcluster con un grafo estático y probabilidad de interacción ajustable.
        
#         :param agents: Lista de agentes en el subcluster.
#         :param topology: Topología del grafo ("scale_free" o "complete").
#         :param interaction_probability: Probabilidad de que una conexión en el grafo genere una interacción.
#         """
#         self.agents = agents
#         self.topology = topology
#         self.cluster = cluster
#         self.graph = self.generate_graph()  # Se genera una vez y no se vuelve a calcular en cada paso

#     def generate_graph(self):
#         """
#         Genera un grafo basado en la topología especificada.
#         """
#         num_agents = len(self.agents)
#         # if num_agents < 2:
#         #     return nx.Graph()

#         if self.topology == "scale_free":
#             m = max(1, min(2, num_agents - 1))
#             graph = nx.barabasi_albert_graph(num_agents, m)
#         elif self.topology == "complete":
#             graph = nx.complete_graph(num_agents)
#         else:
#             raise ValueError(f"Unknown topology: {self.topology}")

#         for i, agent in enumerate(self.agents):
#             graph.nodes[i]["agent"] = agent

#         return graph

#     def remove_agent(self, agent):
#         """
#         Elimina un agente del grafo cuando fallece para evitar futuras interacciones.
#         """
#         for node in list(self.graph.nodes):
#             if self.graph.nodes[node]["agent"] == agent:
#                 self.graph.remove_node(node)
#                 break

#     def simulate_interactions(self, agents):
#         """
#         Simula interacciones dentro del subcluster basándose en la probabilidad de interacción.
#         """
#         interactions = []
#         for edge in list(self.graph.edges):
#             agent1 = self.graph.nodes[edge[0]]['agent']
#             agent2 = self.graph.nodes[edge[1]]['agent']
            
#             #Evitar interacciones con agentes fallecidos
#             if self.cluster.cluster_type == "shopping":
#                 if agents[agent1.agent_id].infection_status['state'] == State.DECEASED or agents[agent1.agent_id].is_hospitalized or agents[agent1.agent_id].is_isolated:
#                     self.update_shopping_agents(agent1)
#                     continue
#                 elif agents[agent2.agent_id].infection_status['state'] == State.DECEASED or agents[agent2.agent_id].is_hospitalized or agents[agent2.agent_id].is_isolated:
#                     self.update_shopping_agents(agent2)
#                     continue    
#             if agents[agent1.agent_id].infection_status["state"] == State.DECEASED or agents[agent2.agent_id].infection_status["state"] == State.DECEASED:
#                 continue

#             if agents[agent1.agent_id].is_hospitalized or agents[agent2.agent_id].is_hospitalized or agents[agent1.agent_id].is_isolated or agents[agent2.agent_id].is_isolated:
#                 continue

#             if random.random() < self.cluster.interaction_probability:
#                 interactions.append((agent1.agent_id, agent2.agent_id))
        
#         return interactions
    
#     def adjust_interaction_probability(self, new_probability):
#         """
#         Permite ajustar la probabilidad de interacción sin modificar la estructura del grafo.
#         """
#         self.interaction_probability = new_probability

#     def update_shopping_agents(self, agent):
#         """
#         Actualiza la lista de compradores si un agente fallece, está hospitalizado o aislado.
#         """
#         household_id = agent.household_id
#         household_members = [member for member in agent.household if member.agent_id != agent.agent_id]
#         best_candidate = None
#         best_age = -1  # Almacena la mejor edad encontrada

#         # Buscar el mejor representante en una sola iteración
#         for member in household_members:
#             if member.infection_status["state"] == State.DECEASED or member.is_hospitalized or member.is_isolated:
#                 continue  # Saltar agentes no disponibles

#             if member.age >= 18:
#                 best_candidate = member  # Adulto disponible, mejor opción
#                 break  # No es necesario seguir buscando

#             if member.age > best_age:  # Guardar el mejor candidato si no es adulto
#                 best_candidate = member
#                 best_age = member.age

#         # Remover el agente del grafo
#         for node in list(self.graph.nodes):
#             if self.graph.nodes[node]["agent"] == agent:
#                 self.graph.remove_node(node)
#                 self.agents.remove(agent)
#                 break

#         # Si se encontró un nuevo representante, actualizar el cluster
#         if best_candidate and best_age >= 12:
#             self.agents.append(best_candidate)  # Agregar al nuevo representante


#         self.graph = self.generate_graph()  # Regenerar el grafo con el nuevo agente
#             # new_node = len(self.graph.nodes)  # Nuevo índice de nodo en el grafo
#             # self.graph.add_node(new_node, agent=best_candidate)

#             # Conectar con vecinos existentes en la red de compras
#             # for neighbor in self.graph.nodes:
#             #     if random.random() < 0.5:  # Probabilidad arbitraria de reconectar
#             #         self.graph.add_edge(new_node, neighbor)



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

    def simulate_interactions(self, time_period, agents):
        """
        Simula interacciones en todos los subclusters durante un período activo.
        """
        interactions = []
        if not self.lockdown_is_active and time_period in self.active_periods:
            for subcluster in self.subclusters:
                interactions.extend(subcluster.simulate_interactions(agents))
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
    def __init__(self, city_data):
        self.data = city_data
        self.total_companies = city_data["total_empresas"]
        self.total_stores = city_data["total_tiendas"]
        self.municipal_data = city_data["municipios"]
    
    def generate_clusters(self, agents):
        return {
            "home": self.generate_home_clusters(agents),
            "school": self.generate_school_clusters(agents),
            "work": self.generate_work_clusters(agents),
            "shopping": self.generate_shopping_clusters(agents),
        }
    
    def generate_home_clusters(self, agents):
        home_subclusters = []
        household_id_counter = 0  # Contador único para asignar household_id
        cluster = ClusterWithSubclusters(home_subclusters, "home", ["morning", "night"], interaction_probability=random.uniform(0.7, 0.1))

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

                # Asegurar que haya al menos un adulto y un menor si es posible
                if not any(agent.age >= 18 for agent in household_agents):
                    adults = [a for a in unassigned_agents if a.age >= 18]
                    if adults:
                        household_agents.append(adults.pop(0))
                        unassigned_agents.remove(household_agents[-1])
                
                if not any(agent.age < 18 for agent in household_agents):
                    children = [a for a in unassigned_agents if a.age < 18]
                    if children:
                        household_agents.append(children.pop(0))
                        unassigned_agents.remove(household_agents[-1])

                # Asignar un household_id único a todos los agentes en este hogar
                for agent in household_agents:
                    agent.household_id = household_id_counter
                    agent.household = household_agents
                household_id_counter += 1  # Incrementar para el siguiente hogar

                home_subclusters.append(Subcluster(household_agents, cluster, topology="complete"))

        cluster.subclusters = home_subclusters
        print("Home clusters generated with a more realistic composition")
        return cluster

    

    def generate_work_clusters(self, agents):
        work_subclusters = []
        cluster = ClusterWithSubclusters(work_subclusters, "work", ["daytime"], interaction_probability=random.uniform(0.3, 0.6))
        
        # Filtramos los trabajadores
        workers = [agent for agent in agents if agent.occupation == "worker"]
        random.shuffle(workers)  # Aleatorizamos el orden de los trabajadores para evitar sesgos
        
        total_workers = len(workers)
        if total_workers == 0:
            print("No hay trabajadores disponibles para asignar a empresas.")
            return cluster
        
        # Distribuir los trabajadores por municipio
        municipal_worker_distribution = {municipio: [] for municipio in self.municipal_data}
        
        # Asignar trabajadores a los municipios en función de su campo 'municipio'
        for worker in workers:
            municipio = worker.municipio
            if municipio in municipal_worker_distribution:
                municipal_worker_distribution[municipio].append(worker)
        
        # Generar las empresas por municipio según el dato en "empresas"
        for municipio, worker_list in municipal_worker_distribution.items():
            # Obtener la cantidad de empresas en este municipio
            num_companies = self.municipal_data[municipio].get("Centros_Laborales", 0)
            if num_companies == 0:
                continue  # Si no hay empresas en el municipio, no asignamos trabajadores
            
            # Calcular el número promedio de trabajadores por empresa en este municipio
            total_workers_in_municipio = len(worker_list)
            avg_size = total_workers_in_municipio // num_companies
            remaining_workers = total_workers_in_municipio % num_companies

            # Inicializar el tamaño de las empresas para este municipio
            company_sizes = [avg_size for _ in range(num_companies)]

            # Distribuir los trabajadores restantes de manera uniforme entre las empresas
            for i in range(remaining_workers):
                company_sizes[i % num_companies] += 1
            
            # Asignar los trabajadores a las empresas del municipio
            unassigned_workers = worker_list.copy()
            
            for size in company_sizes:
                if not unassigned_workers:
                    break
                size = min(size, len(unassigned_workers))  # No asignar más trabajadores de los que hay disponibles
                company_workers = unassigned_workers[:size]
                unassigned_workers = unassigned_workers[size:]

                # Crear un subcluster para la empresa con los trabajadores asignados
                work_subclusters.append(Subcluster(company_workers, cluster, topology="scale_free"))
            
        cluster.subclusters = work_subclusters
        print(f"Se generaron: {len(cluster.subclusters)} empresas")
        return cluster

    def generate_shopping_clusters(self, agents):
        shopping_subclusters = []
        external_store_factor = self.total_stores
        
        # Crear el cluster de compras con su interacción
        cluster = ClusterWithSubclusters(shopping_subclusters, "shopping", ["evening"], interaction_probability=random.uniform(0.1, 0.4))
        
        # Seleccionar un representante por hogar mayor de 18 años
        household_representatives = {}
        for agent in agents:  
            if agent.household_id not in household_representatives and agent.age >= 18:
                household_representatives[agent.household_id] = agent
        
        shoppers = list(household_representatives.values())
        random.shuffle(shoppers)
        
        # Calcular el número de tiendas en base a un factor externo o por defecto en función de los compradores
        if external_store_factor is not None:
            num_shopping_centers = max(1, min(external_store_factor, len(shoppers) // 50))
        else:
            num_shopping_centers = min(self.total_stores, max(1, len(shoppers) // 50))
        
        # Ajustar tamaños dinámicos de las tiendas según la cantidad de compradores
        total_shoppers = len(shoppers)
        if total_shoppers < num_shopping_centers * 15:
            shopping_sizes = [1 for _ in range(total_shoppers)]  # Si hay más tiendas que compradores
        else:
            avg_size = total_shoppers // num_shopping_centers
            shopping_sizes = [avg_size for _ in range(num_shopping_centers)]
            
            remaining_shoppers = total_shoppers - sum(shopping_sizes)
            for i in range(remaining_shoppers):
                shopping_sizes[i % num_shopping_centers] += 1  # Distribuir compradores restantes
        
        # Asignar compradores a las tiendas
        unassigned_shoppers = shoppers.copy()
        for size in shopping_sizes:
            if not unassigned_shoppers:
                break
            size = min(size, len(unassigned_shoppers))
            shopping_agents = unassigned_shoppers[:size]
            unassigned_shoppers = unassigned_shoppers[size:]
            shopping_subclusters.append(Subcluster(shopping_agents, cluster, topology="scale_free"))
        
        cluster.subclusters = shopping_subclusters
        print(f"Se generaron {len(cluster.subclusters)} tiendas")
        return cluster

    def generate_school_clusters(self, agents):
        school_subclusters = []
        cluster = ClusterWithSubclusters(school_subclusters, "school", ["daytime"], interaction_probability=random.uniform(0.5, 0.9))
        
        # Mapeo de tipos de escuelas a rangos de edad
        school_age_mapping = {
            "Círculos infantiles": (0, 5),
            "Primaria": (6, 11),
            "Media": (12, 14),
            "Secundaria básica": (15, 17),
            "Preuniversitario": (18, 19),
            "Técnica y profesional": (18, 22)
        }

        # Filtrar estudiantes por rango de edad y asignarlos a escuelas por municipio
        for municipio, data in self.municipal_data.items():
            # Obtener el número de escuelas por tipo en este municipio
            schools_in_municipio = data.get("Escuelas", {})
            
            for school_type, num_schools in schools_in_municipio.items():
                if school_type not in school_age_mapping:
                    print(f"Advertencia: El tipo de escuela '{school_type}' no tiene un rango de edad asignado.")
                    continue  # Saltar tipos de escuelas no definidos en el mapeo

                # Obtener el rango de edad para el tipo de escuela actual
                age_range = school_age_mapping[school_type]
                
                # Filtrar estudiantes en el rango de edad correspondiente y que pertenezcan al municipio
                students = [
                    agent for agent in agents 
                    if agent.occupation == "student" 
                    and age_range[0] <= agent.age <= age_range[1]
                    and agent.municipio == municipio
                ]
                random.shuffle(students)  # Aleatorizar estudiantes para evitar sesgos

                # Si no hay estudiantes para este tipo de escuela, se omite
                if not students:
                    print(f"No se encontraron estudiantes para '{school_type}' en el rango de edad {age_range} en el municipio {municipio}.")
                    continue

                # Crear el número de escuelas del tipo actual
                school_sizes = self._get_school_sizes(num_schools, len(students))
                unassigned_students = students.copy()

                # Asignar estudiantes a las escuelas generadas
                for size in school_sizes:
                    if not unassigned_students:
                        break  # No hay más estudiantes para asignar

                    size = min(size, len(unassigned_students))  # Asegurar que no exceda el número de estudiantes disponibles
                    school_agents = unassigned_students[:size]
                    unassigned_students = unassigned_students[size:]

                    # Crear un subcluster para la escuela con los estudiantes asignados
                    school_subclusters.append(Subcluster(school_agents, cluster, topology="scale_free"))

        # Asignar los subclusters generados al cluster general
        cluster.subclusters = school_subclusters
        print(f"Se generaron {len(cluster.subclusters)} escuelas.")
        return cluster
    # def generate_school_clusters(self, agents):
    #     school_subclusters = []
    #     cluster = ClusterWithSubclusters(school_subclusters, "school", ["daytime"], interaction_probability=random.uniform(0.5, 0.9))
        
    #     # Mapeo de tipos de escuelas a rangos de edad
    #     school_age_mapping = {
    #         "Círculos infantiles": (0, 5),
    #         "Primaria": (6, 11),
    #         "Media": (12, 14),
    #         "Secundaria": (15, 17),
    #         "Preuniversitario": (18, 19),
    #         "Tecnica y profesional": (18, 22)
    #     }

    #     # Obtener el número total de escuelas por tipo desde el diccionario general
    #     total_schools = self.data.get("Escuelas_Total", {})
        
    #     # Filtrar estudiantes por rango de edad y asignarlos a escuelas
    #     for school_type, num_schools in total_schools.items():
    #         if school_type not in school_age_mapping:
    #             print(f"Advertencia: El tipo de escuela '{school_type}' no tiene un rango de edad asignado.")
    #             continue  # Saltar tipos de escuelas no definidos en el mapeo

    #         # Obtener el rango de edad para el tipo de escuela actual
    #         age_range = school_age_mapping[school_type]
            
    #         # Filtrar estudiantes en el rango de edad correspondiente
    #         students = [
    #             agent for agent in agents 
    #             if agent.occupation == "student" 
    #             and age_range[0] <= agent.age <= age_range[1]
    #         ]
    #         random.shuffle(students)  # Aleatorizar estudiantes para evitar sesgos

    #         # Si no hay estudiantes para este tipo de escuela, se omite
    #         if not students:
    #             print(f"No se encontraron estudiantes para '{school_type}' en el rango de edad {age_range}.")
    #             continue

    #         # Crear el número de escuelas del tipo actual
    #         school_sizes = self._get_school_sizes(num_schools, len(students))
    #         unassigned_students = students.copy()

    #         # Asignar estudiantes a las escuelas generadas
    #         for size in school_sizes:
    #             if not unassigned_students:
    #                 break  # No hay más estudiantes para asignar

    #             size = min(size, len(unassigned_students))  # Asegurar que no exceda el número de estudiantes disponibles
    #             school_agents = unassigned_students[:size]
    #             unassigned_students = unassigned_students[size:]

    #             # Crear un subcluster para la escuela con los estudiantes asignados
    #             school_subclusters.append(Subcluster(school_agents, cluster, topology="scale_free"))

    #     # Asignar los subclusters generados al cluster general
    #     cluster.subclusters = school_subclusters
    #     print(f"Se generaron {len(cluster.subclusters)} escuelas.")
    #     return cluster

    def _get_school_sizes(self, num_schools, total_students):
        """Calcula los tamaños de las escuelas basándose en el número de estudiantes y el número de escuelas."""
        if num_schools == 0:
            return []  # Si no hay escuelas, no se puede generar tamaño de escuela
        
        avg_size = total_students // num_schools  # Tamaño promedio de la escuela
        remaining_students = total_students % num_schools  # Estudiantes restantes por distribuir

        # Inicializamos los tamaños de las escuelas
        school_sizes = [avg_size for _ in range(num_schools)]

        # Distribuir los estudiantes restantes de manera uniforme entre las escuelas
        for i in range(remaining_students):
            school_sizes[i % num_schools] += 1

        return school_sizes




    # def generate_school_clusters(self, agents):
    #     school_subclusters = []
    #     cluster = ClusterWithSubclusters(school_subclusters, "school", ["daytime"], interaction_probability=random.uniform(0.5, 0.9))
        
    #     # Mapeo de tipos de escuelas a rangos de edad
    #     school_age_mapping = {
    #         "Círculos infantiles": (0, 5),
    #         "Primaria": (6, 11),
    #         "Media": (12, 14),
    #         "Secundaria": (15, 17),
    #         "Preuniversitario": (18, 19),
    #         "Tecnica y profesional": (18, 22)
    #     }

    #     # Obtener el número total de escuelas por tipo desde el diccionario general
    #     total_schools = self.data.get("Escuelas_Total", {})
        
    #     # Filtrar estudiantes por rango de edad y asignarlos a escuelas
    #     for school_type, num_schools in total_schools.items():
    #         if school_type not in school_age_mapping:
    #             continue  # Saltar tipos de escuelas no definidos en el mapeo

    #         age_range = school_age_mapping[school_type]
            
    #         # Filtrar estudiantes en el rango de edad correspondiente
    #         students = [
    #             agent for agent in agents 
    #             if agent.occupation == "student" 
    #             and age_range[0] <= agent.age <= age_range[1]
    #         ]
    #         random.shuffle(students)

    #         # Crear escuelas del tipo actual
    #         school_sizes = [random.randint(20, 50) for _ in range(int(num_schools))]
    #         unassigned_students = students.copy()

    #         for size in school_sizes:
    #             if not unassigned_students:
    #                 break  # No hay más estudiantes para asignar

    #             size = min(size, len(unassigned_students))  # Asegurar que no exceda el número de estudiantes disponibles
    #             school_agents = unassigned_students[:size]
    #             unassigned_students = unassigned_students[size:]

    #             # Crear un subcluster para la escuela
    #             school_subclusters.append(Subcluster(school_agents, cluster, topology="scale_free"))

    #     cluster.subclusters = school_subclusters
    #     print(f"Se generaron : {len(cluster.subclusters)} escuelas")
    #     return cluster
    # def generate_school_clusters(self, agents):
    #     school_subclusters = []
    #     cluster = ClusterWithSubclusters(school_subclusters, "school", ["daytime"], interaction_probability= random.uniform(0.5,0.9))
    #     school_age_mapping = {
    #         "Circulos infantiles": (0, 5),
    #         "Primaria": (6, 11),
    #         "Secundaria basica": (12, 14),
    #         "Preuniversitario": (15, 17),
    #         "Tecnica y profesional": (18, 22)
    #     }

    #     for municipio, data in self.municipal_data.items():
    #         if "Escuelas" not in data:
    #             continue
            
    #         for school_type, num_schools in data["Escuelas"].items():
    #             if school_type not in school_age_mapping:
    #                 continue
    #             age_range = school_age_mapping[school_type]

    #             students = [agent for agent in agents if agent.municipio == municipio and agent.occupation == "student" and age_range[0] <= agent.age <= age_range[1]]
    #             random.shuffle(students)

    #             school_sizes = [random.randint(20, 50) for _ in range(int(num_schools))]
    #             unassigned_students = students.copy()

    #             for size in school_sizes:
    #                 if not unassigned_students:
    #                     break
    #                 size = min(size, len(unassigned_students))
    #                 school_agents = unassigned_students[:size]
    #                 unassigned_students = unassigned_students[size:]
    #                 school_subclusters.append(Subcluster(school_agents,cluster, topology="scale_free"))

    #     cluster.subclusters = school_subclusters
    #     print("School clusters generated")
    #     return cluster