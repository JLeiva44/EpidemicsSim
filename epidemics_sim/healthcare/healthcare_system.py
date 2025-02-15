import random
from epidemics_sim.healthcare.reporter import SimulationAnalyzer
from epidemics_sim.policies.vaccination_policy import VaccinationPolicy
from epidemics_sim.policies.lockdown_policy import LockdownPolicy
from epidemics_sim.policies.mask_policy import MaskUsagePolicy
from epidemics_sim.policies.social_distancing_policy import SocialDistancingPolicy
from epidemics_sim.agents.base_agent import State

class HealthcareSystem:
    def __init__(self, hospital_capacity, isolation_capacity, policies=[], demografics={}):
        self.hospital_capacity = hospital_capacity
        self.isolation_capacity = isolation_capacity
        self.hospitalized = []
        self.isolated = []
        self.demografics = demografics
        self.analyzer = SimulationAnalyzer()
        self.policies = policies
        self.active_policies = {policy: False for policy in self.policies}
        self.policy_counters = {policy: 0 for policy in self.policies}
        self.days_since_last_evaluation = 0
        self.daily_cases = []  # Para almacenar los casos diarios
        self.daily_deaths = []  # Para almacenar las muertes diarias
        self.municipality_data = {
            "infected" : {
                mun: 0 for mun in demografics.keys()},
            "deceased" :{ mun : 0 for mun in demografics.keys()   } 
        }
        self.municipality_diary_data = {
            "infected" : {
                mun: 0 for mun in demografics.keys()},
            "deceased" :{ mun : 0 for mun in demografics.keys()   } 
            }
        # Diccionario para estadísticas diarias
        self.daily_stats = {
            "new_cases": 0,
            "new_deaths": 0,
            "new_recovered": 0,
        }

        # Diccionario para estadísticas acumuladas
        self.cumulative_stats = {
            "susceptible": 0,
            "infected": 0,
            "recovered": 0,
            "deceased": 0,
            "infected_by_severity": {
                "asymptomatic": 0,
                "mild": 0,
                "moderate": 0,
                "severe": 0,
                "critical": 0,
            },
            "hospitalized": 0,
            "hospital_capacity" : hospital_capacity
        }
        self.infected = []
        self.recovered = []
        self.deceased = []


    def collect_health_statistics(self, agents):
        """
        Recopila estadísticas de salud a partir de la lista de agentes.

        :param agents: Lista de agentes en la simulación.
        :return: Un diccionario con las estadísticas recopiladas.
        """
        daily = {
            "new_cases": 0,
            "new_deaths": 0,
            "new_recovered": 0,
        }
        municipality_diary_data = {
            "infected" : {
                mun: 0 for mun in self.demografics.keys()},
            "deceased" :{ mun : 0 for mun in self.demografics.keys()   } 
            }
        # Limpiar las listas diarias 
        self.infected = [agent for agent in self.infected if agent.infection_status["state"] is State.INFECTED]
        self.recovered = [ agent for agent in self.infected if agent.infection_status["state"] is State.RECOVERED]

        for agent in agents:
            if agent.infection_status["state"] is State.INFECTED and agent.infection_status["days_infected"] >= agent.incubation_period + agent.infection_status["diagnosis_delay"]:
                if agent not in self.infected:
                    daily["new_cases"] += 1
                    municipality_diary_data["infected"][agent.municipio] += 1
                    self.infected.append(agent)
                    severity = agent.infection_status.get("severity", "asymptomatic")
                    self.cumulative_stats["infected_by_severity"][severity] += 1
            elif agent.infection_status["state"] == State.RECOVERED:
                if agent not in self.recovered:
                    daily["new_recovered"] += 1
                    self.recovered.append(agent)
            elif agent.infection_status["state"] == State.DECEASED:
                if agent not in self.deceased:
                    daily["new_deaths"] += 1
                    self.municipality_data["deceased"][agent.municipio] += 1
                    self.deceased.append(agent)

        # Actualizar estadisticas por municipios 
        for mun in self.demografics.keys():
            self.municipality_data["infected"][mun] +=municipality_diary_data["infected"][mun]

        self.municipality_diary_data.update(municipality_diary_data)    


        # Actualizar estadísticas acumuladas
        self.cumulative_stats["infected"] += daily["new_cases"]
        self.cumulative_stats["recovered"] += daily["new_recovered"]
        self.cumulative_stats["deceased"] += daily["new_deaths"]

        # Actualizar estadísticas diarias
        self.daily_stats.update(daily)

    def generate_daily_report(self, day):
        """
        Genera un informe diario basado en las estadísticas recopiladas.

        :param stats: Diccionario con las estadísticas de salud.
        :param day: Día actual de la simulación.
        :return: Un string con el informe formateado.
        """
        report = (
            f"\n=== Resumen Diario (Día {day}) ===\n"
            f"Agentes infectados: {self.daily_stats['new_cases']}\n"
            # f"  - Asintomáticos: {stats['infected_by_severity']['asymptomatic']}\n"
            # f"  - Leves: {stats['infected_by_severity']['mild']}\n"
            # f"  - Moderados: {stats['infected_by_severity']['moderate']}\n"
            # f"  - Graves: {stats['infected_by_severity']['severe']}\n"
            # f"  - Críticos: {stats['infected_by_severity']['critical']}\n"
            f"Agentes recuperados: {self.daily_stats['new_recovered']}\n"
            f"Agentes fallecidos: {self.daily_stats['new_deaths']}\n"
            f"Total infectados: {self.cumulative_stats['infected']}\n"
            f"Total recuperados: {self.cumulative_stats['recovered']}\n"
            f"Total fallecidos: {self.cumulative_stats['deceased']}\n"
            f"Hospitalizados: {self.cumulative_stats['hospitalized']}/{self.cumulative_stats['hospital_capacity']}\n"
            "==============================="
        )
        return report

    def monitor_health_status(self, agents, interactions):
        """
        Monitorea el estado de salud de los agentes y actualiza las estadísticas.
        """
        self.collect_health_statistics(agents)

        # # Calcular casos por municipio
        # for agent in agents:
        #     if (agent.infection_status["state"] is State.INFECTED and
        #     agent.infection_status["days_infected"] >= agent.incubation_period + agent.infection_status["diagnosis_delay"]):
        #         municipio = agent.municipio
        #         if municipio not in self.municipality_data:
        #             self.municipality_data[municipio] = 0
        #         self.municipality_data[municipio] += 1

        self.analyzer.record_daily_stats(self.daily_stats["new_cases"], self.daily_stats["new_deaths"], self.municipality_data["infected"])
        self.daily_cases.append(self.daily_stats["new_cases"])
        self.daily_deaths.append(self.daily_stats["new_deaths"])

        if len(self.daily_stats) > 7:
            self.daily_cases.pop(0)
        if len(self.daily_deaths) > 7:
            self.daily_deaths.pop(0)

        # Actualizar lista de hospitalizados
        for agent in self.hospitalized :
            if agent.infection_status["state"] is not State.INFECTED:
                agent.is_hospitalized = False
                self.hospitalized.pop(agent)

        # Priorizar casos críticos y graves para hospitalización
        prioritized_cases = sorted(
            [a for a in self.infected if a.infection_status["severity"] in ["critical", "severe"] and not a.is_hospitalized],
            key=lambda x: ["critical", "severe"].index(x.infection_status["severity"])
        )

        for agent in prioritized_cases:
            if len(self.hospitalized) < self.hospital_capacity:
                agent.is_hospitalized = True
                self.hospitalized.append(agent)


    def evaluate_policies(self, agents, clusters, day):
        """
        Evalúa la situación epidemiológica y permite al usuario aplicar o remover políticas.
        """
        if self.days_since_last_evaluation < 7:
            self.days_since_last_evaluation += 1
            return

        self.days_since_last_evaluation = 0
        #stats = self.collect_health_statistics(agents)

        # Los stats ahora son de la clase

        total_population = len(agents)
        total_infected = self.cumulative_stats["infected"]
        #infection_rate = total_infected / total_population if total_population > 0 else 0
        hospital_occupancy = self.cumulative_stats["hospitalized"] / self.hospital_capacity
        #hospitalized = self.cumulative_stats["hospitalized"]
        #isolated = len(self.isolated)

        avg_cases_last_7_days = sum(self.daily_cases[-7:]) / min(len(self.daily_cases), 7) if self.daily_cases else 0
        avg_deaths_last_7_days = sum(self.daily_deaths[-7:]) / min(len(self.daily_deaths), 7) if self.daily_deaths else 0

        print("\n📊 Evaluación de la situación epidemiológica (Día", day, ")")
        print(f"Total de hospitalizados: {self.cumulative_stats["hospitalized"]}/{self.hospital_capacity}")
        print("Promedio de casos diarios en los últimos 7 días: {:.2f}".format(avg_cases_last_7_days))
        print("Promedio de muertes diarias en los últimos 7 días: {:.2f}".format(avg_deaths_last_7_days))
        print("Políticas activas:", [p.__name__ for p, active in self.active_policies.items() if active])

        applicable_policies = {
            LockdownPolicy: "Cuarentena",
            SocialDistancingPolicy: "Distanciamiento Social",
            MaskUsagePolicy: "Uso obligatorio de mascarillas",
            VaccinationPolicy: "Campaña de vacunación"
        }

        available_policies = {p: d for p, d in applicable_policies.items() if not self.active_policies.get(p, False)}
        removable_policies = {p: d for p, d in applicable_policies.items() if self.active_policies.get(p, False)}

        self.handle_policy_selection(agents, clusters, available_policies, "Aplicar")
        self.handle_policy_selection(agents, clusters, removable_policies, "Remover")

    def handle_policy_selection(self, agents, clusters, policies, action):
        """
        Maneja la selección de políticas por parte del usuario.
        """
        if not policies:
            return

        print(f"\nSeleccione las políticas a {action.lower()}:")
        for i, (policy, description) in enumerate(policies.items(), 1):
            print(f"{i}️⃣ {description}")
        print("0️⃣ No hacer cambios")

        choices = input(f"Ingrese los números de las políticas a {action.lower()}, separados por comas: ")
        selected_indices = [int(x) for x in choices.split(',') if x.isdigit() and int(x) in range(1, len(policies) + 1)]

        for index in selected_indices:
            policy = list(policies.keys())[index - 1]
            if action == "Aplicar":
                self.enforce_policies(agents, clusters, policy)
            else:
                self.remove_policies(agents, clusters, policy)

    def enforce_policies(self, agents, clusters, policy_type):
        """
        Aplica una política específica.
        """
        for policy in self.policies:
            if isinstance(policy, policy_type):
                policy.enforce(agents, clusters)
                self.active_policies[policy_type] = True
                print(f"✅ {policy_type.__name__} aplicada.")

    def remove_policies(self, agents, clusters, policy_type):
        """
        Remueve una política específica.
        """
        for policy in self.policies:
            if isinstance(policy, policy_type):
                policy.delete(agents, clusters)
                self.active_policies[policy_type] = False
                print(f"🛑 {policy_type.__name__} eliminada.")

    def daily_operations(self, agents, clusters, interactions, day):
        """
        Realiza las operaciones diarias del sistema de salud.
        """
        # Monitorear el estado de salud y recopilar estadísticas
        self.monitor_health_status(agents, interactions)

        # Generar y mostrar el resumen diario
        #stats = self.collect_health_statistics(agents)
        daily_report = self.generate_daily_report(day)
        print(daily_report)

        # Verificar si la política de vacunación está activa y continuar vacunando progresivamente
        if self.active_policies.get(VaccinationPolicy, False):
            for policy in self.policies:
                if isinstance(policy, VaccinationPolicy):
                    total_vaccination = policy.enforce(agents, clusters)  # Continúa vacunando
                    if total_vaccination:
                        self.remove_policies(agents, clusters, VaccinationPolicy)

        # Evaluar políticas cada 7 días
        self.evaluate_policies(agents, clusters, day)
# import random
# from epidemics_sim.healthcare.last import SimulationAnalyzer
# from epidemics_sim.policies.vaccination_policy import VaccinationPolicy
# from epidemics_sim.policies.lockdown_policy import LockdownPolicy
# from epidemics_sim.policies.mask_policy import MaskUsagePolicy
# from epidemics_sim.policies.social_distancing_policy import SocialDistancingPolicy
# from epidemics_sim.agents.base_agent import State

# class HealthcareSystem:
#     def __init__(self, hospital_capacity, isolation_capacity, policies=[], demografics={}):
#         self.hospital_capacity = hospital_capacity
#         self.isolation_capacity = isolation_capacity
#         self.hospitalized = []
#         self.isolated = []
#         self.analyzer = SimulationAnalyzer()
#         self.policies = policies
#         self.active_policies = {policy: False for policy in self.policies}
#         self.policy_counters = {policy: 0 for policy in self.policies}
#         self.days_since_last_evaluation = 0
#         self.daily_cases = []  # Para almacenar los casos diarios
#         self.daily_deaths = []  # Para almacenar las muertes diarias
#         self.municipality_data = {mun: 0 for mun in demografics.keys()}
#         self.municipality_diary_data = {mun: [] for mun in demografics.keys()}

#     def collect_health_statistics(self, agents):
#         """
#         Recopila estadísticas de salud a partir de la lista de agentes.

#         :param agents: Lista de agentes en la simulación.
#         :return: Un diccionario con las estadísticas recopiladas.
#         """
#         stats = {
#             "total_agents": len(agents),
#             "susceptible": 0,
#             "infected": 0,
#             "recovered": 0,
#             "deceased": 0,
#             "infected_by_severity": {
#                 "incubation_period":0,
#                 "asymptomatic": 0,
#                 "mild": 0,
#                 "moderate": 0,
#                 "severe": 0,
#                 "critical": 0
#             },
#             "hospitalized": len(self.hospitalized),
#             "hospital_capacity": self.hospital_capacity,
#             "available_beds": self.hospital_capacity - len(self.hospitalized)
#         }

#         for agent in agents:
#             if agent.infection_status["state"] == State.SUSCEPTIBLE:
#                 stats["susceptible"] += 1
#             elif agent.state == State.INFECTED:
#                 stats["infected"] += 1
#                 severity = agent.infection_status.get("severity", "asymptomatic")
#                 if severity is None : 
#                     severity = "incubation_period"
#                 stats["infected_by_severity"][severity] += 1
#             elif agent.state == State.RECOVERED:
#                 stats["recovered"] += 1
#             elif agent.state == State.DECEASED:
#                 stats["deceased"] += 1

#         return stats

#     def generate_daily_report(self, stats, day):
#         """
#         Genera un informe diario basado en las estadísticas recopiladas.

#         :param stats: Diccionario con las estadísticas de salud.
#         :param day: Día actual de la simulación.
#         :return: Un string con el informe formateado.
#         """
#         report = (
#             f"\n=== Resumen Diario (Día {day}) ===\n"
#             f"Agentes susceptibles: {stats['susceptible']}\n"
#             f"Agentes infectados: {stats['infected']}\n"
#             f"  - Asintomáticos: {stats['infected_by_severity']['asymptomatic']}\n"
#             f"  - Leves: {stats['infected_by_severity']['mild']}\n"
#             f"  - Moderados: {stats['infected_by_severity']['moderate']}\n"
#             f"  - Graves: {stats['infected_by_severity']['severe']}\n"
#             f"  - Críticos: {stats['infected_by_severity']['critical']}\n"
#             f"Agentes recuperados: {stats['recovered']}\n"
#             f"Agentes fallecidos: {stats['deceased']}\n"
#             f"Hospitalizados: {stats['hospitalized']}/{stats['hospital_capacity']}\n"
#             f"Camas disponibles: {stats['available_beds']}\n"
#             "==============================="
#         )
#         return report

#     def monitor_health_status(self, agents, interactions):
#         """
#         Monitorea el estado de salud de los agentes y actualiza las estadísticas.
#         """
#         stats = self.collect_health_statistics(agents)
#         new_cases = stats["infected"]
#         new_deaths = stats["deceased"]

#         # Calcular casos por municipio
#         for agent in agents:
#             if agent.infection_status["state"] is State.INFECTED:
#                 municipio = agent.municipio
#                 if municipio not in self.municipality_data:
#                     self.municipality_data[municipio] = 0
#                 self.municipality_data[municipio] += 1

#         self.analyzer.record_daily_stats(new_cases, new_deaths, self.municipality_data)
#         self.daily_cases.append(new_cases)
#         self.daily_deaths.append(new_deaths)

#         if len(self.daily_cases) > 7:
#             self.daily_cases.pop(0)
#         if len(self.daily_deaths) > 7:
#             self.daily_deaths.pop(0)

#         # Actualizar lista de hospitalizados
#         self.hospitalized = [a for a in self.hospitalized if a.infection_status["state"] not in [State.RECOVERED, State.DECEASED]]

#         # Priorizar casos críticos y graves para hospitalización
#         prioritized_cases = sorted(
#             [a for a in agents if a.infection_status["severity"] in ["critical", "severe"] and not a.is_hospitalized],
#             key=lambda x: ["critical", "severe"].index(x.infection_status["severity"])
#         )

#         for agent in prioritized_cases:
#             if len(self.hospitalized) < self.hospital_capacity:
#                 agent.is_hospitalized = True
#                 self.hospitalized.append(agent)

#     def evaluate_policies(self, agents, clusters, day):
#         """
#         Evalúa la situación epidemiológica y permite al usuario aplicar o remover políticas.
#         """
#         if self.days_since_last_evaluation < 7:
#             self.days_since_last_evaluation += 1
#             return

#         self.days_since_last_evaluation = 0
#         stats = self.collect_health_statistics(agents)
#         #weekly_report = self.generate_weekly_report(stats)
#         #print(weekly_report)

#         total_population = len(agents)
#         total_infected = stats["infected"]
#         infection_rate = total_infected / total_population if total_population > 0 else 0
#         hospital_occupancy = stats["hospitalized"] / self.hospital_capacity
#         hospitalized = stats["hospitalized"]
#         isolated = len(self.isolated)

#         avg_cases_last_10_days = sum(self.daily_cases[-7:]) / min(len(self.daily_cases), 7) if self.daily_cases else 0
#         avg_deaths_last_10_days = sum(self.daily_deaths[-7:]) / min(len(self.daily_deaths), 7) if self.daily_deaths else 0

#         print("\n📊 Evaluación de la situación epidemiológica (Día", day, ")")
#         print("Tasa de infección actual: {:.2%}".format(infection_rate))
#         print(f"Total de hospitalizados: {hospitalized}/{self.hospital_capacity}")
#         print("Promedio de casos diarios en los últimos 7 días: {:.2f}".format(avg_cases_last_10_days))
#         print("Promedio de muertes diarias en los últimos 7 días: {:.2f}".format(avg_deaths_last_10_days))
#         print("Políticas activas:", [p.__name__ for p, active in self.active_policies.items() if active])

#         applicable_policies = {
#             LockdownPolicy: "Cuarentena",
#             SocialDistancingPolicy: "Distanciamiento Social",
#             MaskUsagePolicy: "Uso obligatorio de mascarillas",
#             VaccinationPolicy: "Campaña de vacunación"
#         }

#         available_policies = {p: d for p, d in applicable_policies.items() if not self.active_policies.get(p, False)}
#         removable_policies = {p: d for p, d in applicable_policies.items() if self.active_policies.get(p, False)}

#         self.handle_policy_selection(agents, clusters, available_policies, "Aplicar")
#         self.handle_policy_selection(agents, clusters, removable_policies, "Remover")

#     def handle_policy_selection(self, agents, clusters, policies, action):
#         """
#         Maneja la selección de políticas por parte del usuario.
#         """
#         if not policies:
#             return

#         print(f"\nSeleccione las políticas a {action.lower()}:")
#         for i, (policy, description) in enumerate(policies.items(), 1):
#             print(f"{i}️⃣ {description}")
#         print("0️⃣ No hacer cambios")

#         choices = input(f"Ingrese los números de las políticas a {action.lower()}, separados por comas: ")
#         selected_indices = [int(x) for x in choices.split(',') if x.isdigit() and int(x) in range(1, len(policies) + 1)]

#         for index in selected_indices:
#             policy = list(policies.keys())[index - 1]
#             if action == "Aplicar":
#                 self.enforce_policies(agents, clusters, policy)
#             else:
#                 self.remove_policies(agents, clusters, policy)

#     def enforce_policies(self, agents, clusters, policy_type):
#         """
#         Aplica una política específica.
#         """
#         for policy in self.policies:
#             if isinstance(policy, policy_type):
#                 policy.enforce(agents, clusters)
#                 self.active_policies[policy_type] = True
#                 print(f"✅ {policy_type.__name__} aplicada.")

#     def remove_policies(self, agents, clusters, policy_type):
#         """
#         Remueve una política específica.
#         """
#         for policy in self.policies:
#             if isinstance(policy, policy_type):
#                 policy.delete(agents, clusters)
#                 self.active_policies[policy_type] = False
#                 print(f"🛑 {policy_type.__name__} eliminada.")

#     def daily_operations(self, agents, clusters, interactions, day):
#         """
#         Realiza las operaciones diarias del sistema de salud.
#         """
#         # Monitorear el estado de salud y recopilar estadísticas
#         self.monitor_health_status(agents, interactions)

#         # Generar y mostrar el resumen diario
#         stats = self.collect_health_statistics(agents)
#         daily_report = self.generate_daily_report(stats, day)
#         print(daily_report)

#         # Verificar si la política de vacunación está activa y continuar vacunando progresivamente
#         if self.active_policies.get(VaccinationPolicy, False):
#             for policy in self.policies:
#                 if isinstance(policy, VaccinationPolicy):
#                     total_vaccination = policy.enforce(agents, clusters)  # Continúa vacunando
#                     if total_vaccination:
#                         self.remove_policies(agents, clusters, VaccinationPolicy)

#         # Evaluar políticas cada 7 días
#         self.evaluate_policies(agents, clusters, day)

# import random
# from epidemics_sim.healthcare.deep2 import SimulationAnalyzer
# from epidemics_sim.policies.vaccination_policy import VaccinationPolicy
# from epidemics_sim.policies.lockdown_policy import LockdownPolicy
# from epidemics_sim.policies.mask_policy import MaskUsagePolicy
# from epidemics_sim.policies.social_distancing_policy import SocialDistancingPolicy
# from epidemics_sim.agents.base_agent import State

# class HealthcareSystem:
#     def __init__(self, hospital_capacity, isolation_capacity, policies=[], demografics = {}):
#         self.hospital_capacity = hospital_capacity
#         self.isolation_capacity = isolation_capacity
#         self.hospitalized = []
#         self.isolated = []
#         self.analyzer = SimulationAnalyzer()
#         self.policies = policies
#         self.active_policies = {policy: False for policy in self.policies}
#         self.policy_counters = {policy: 0 for policy in self.policies}
#         self.days_since_last_evaluation = 0
#         self.daily_cases = []  # Para almacenar los casos diarios
#         self.daily_deaths = []  # Para almacenar las muertes diarias
#         self.municipality_data = {mun : 0 for mun in demografics.keys()}
#         self.municipality_diary_data = {mun : [] for mun in demografics.keys()} 

#     def monitor_health_status(self, agents, interactions):
#         # new_cases = sum(1 for agent in agents if agent.infection_status["state"] == State.INFECTED)
#         # new_deaths = sum(1 for agent in agents if agent.infection_status["state"] == State.DECEASED)
#         new_cases = 0
#         new_deaths = 0

#         # Calcular casos por municipio
#         for agent in agents:
#             if agent.infection_status["state"] is State.INFECTED:
#                 new_cases += 1
#                 municipio = agent.municipio
#                 if municipio == "PLAYA":
#                     g=7
                
#                 if municipio not in self.municipality_data:
#                     self.municipality_data[municipio] = 0
#                 self.municipality_data[municipio] += 1
#                 #self.municipality_diary_data[municipio]
#             elif agent.infection_status["state"] is State.DECEASED:
#                 new_deaths += 1
#         self.analyzer.record_daily_stats(new_cases, new_deaths, self.municipality_data)
        
#         self.daily_cases.append(new_cases)
#         self.daily_deaths.append(new_deaths)
        
#         if len(self.daily_cases) > 10:
#             self.daily_cases.pop(0)
#         if len(self.daily_deaths) > 10:
#             self.daily_deaths.pop(0)
        
#         self.hospitalized = [a for a in self.hospitalized if a.infection_status["state"] is not State.RECOVERED or a.infection_status["state"] is not State.DECEASED]
#         # self.isolated = [a for a in self.isolated if a.infection_status["state"] is not State.RECOVERED or a.infection_status["state"] is not State.DECEASED]
        
#         prioritized_cases = sorted(
#             [a for a in agents if a.infection_status["severity"] in ["critical", "severe"] and not a.is_hospitalized and not a.is_isolated],
#             key=lambda x: ["critical", "severe"].index(x.infection_status["severity"])
#         )


#         for agent in prioritized_cases:
#             if len(self.hospitalized) < self.hospital_capacity:
#                 agent.is_hospitalized = True
#                 self.hospitalized.append(agent)
#         #         agent.is_hospitalized, agent.is_isolated = True, False
#         #     elif len(self.isolated) < self.isolation_capacity:
#         #         self.isolated.append(agent)
#         #         agent.is_isolated, agent.is_hospitalized = True, False

#     def evaluate_policies(self, agents, clusters, day):
#         if self.days_since_last_evaluation < 7:
#             self.days_since_last_evaluation += 1
#             return

#         self.days_since_last_evaluation = 0
#         total_population = len(agents)
#         total_infected = sum(1 for agent in agents if agent.infection_status["state"] is State.INFECTED)
#         infection_rate = total_infected / total_population if total_population > 0 else 0
#         hospital_occupancy = len(self.hospitalized) / self.hospital_capacity
#         hospitalized = len(self.hospitalized)
#         isolated = len(self.isolated)
        
#         avg_cases_last_10_days = sum(self.daily_cases[-10:]) / min(len(self.daily_cases), 7) if self.daily_cases else 0
#         avg_deaths_last_10_days = sum(self.daily_deaths[-10:]) / min(len(self.daily_deaths), 7) if self.daily_deaths else 0

#         print("\n📊 Evaluación de la situación epidemiológica (Día", day, ")")
#         print("Tasa de infección actual: {:.2%}".format(infection_rate))
#         print(f"Total de hospitalizados: {hospitalized}/{self.hospital_capacity}")
#         # print(f"Total de aislados: {isolated}/{self.isolation_capacity}")
#         # print("Ocupación hospitalaria: {:.2%}".format(hospital_occupancy))
#         print("Promedio de casos diarios en los últimos 7 días: {:.2f}".format(avg_cases_last_10_days))
#         print("Promedio de muertes diarias en los últimos 7 días: {:.2f}".format(avg_deaths_last_10_days))
#         print("Políticas activas:", [p.__name__ for p, active in self.active_policies.items() if active])

#         applicable_policies = {
#             LockdownPolicy: "Cuarentena",
#             SocialDistancingPolicy: "Distanciamiento Social",
#             MaskUsagePolicy: "Uso obligatorio de mascarillas",
#             VaccinationPolicy: "Campaña de vacunación"
#         }

#         available_policies = {p: d for p, d in applicable_policies.items() if not self.active_policies.get(p, False)}
#         removable_policies = {p: d for p, d in applicable_policies.items() if self.active_policies.get(p, False)}

#         self.handle_policy_selection(agents, clusters, available_policies, "Aplicar")
#         self.handle_policy_selection(agents, clusters, removable_policies, "Remover")

#     def handle_policy_selection(self, agents, clusters, policies, action):
#         if not policies:
#             return

#         print(f"\nSeleccione las políticas a {action.lower()}:")
#         for i, (policy, description) in enumerate(policies.items(), 1):
#             print(f"{i}️⃣ {description}")
#         print("0️⃣ No hacer cambios")

#         choices = input(f"Ingrese los números de las políticas a {action.lower()}, separados por comas: ")
#         selected_indices = [int(x) for x in choices.split(',') if x.isdigit() and int(x) in range(1, len(policies) + 1)]

#         for index in selected_indices:
#             policy = list(policies.keys())[index - 1]
#             if action == "Aplicar":
#                 self.enforce_policies(agents, clusters, policy)
#             else:
#                 self.remove_policies(agents, clusters, policy)

#     def enforce_policies(self, agents, clusters, policy_type):
#         for policy in self.policies:
#             if isinstance(policy, policy_type):
#                 policy.enforce(agents, clusters)
#                 self.active_policies[policy_type] = True
#                 print(f"✅ {policy_type.__name__} aplicada.")

#     def remove_policies(self, agents, clusters, policy_type):
#         for policy in self.policies:
#             if isinstance(policy, policy_type):
#                 policy.delete(agents, clusters)
#                 self.active_policies[policy_type] = False
#                 print(f"🛑 {policy_type.__name__} eliminada.")

    
#     def daily_operations(self, agents, clusters, interactions, day):
#         self.monitor_health_status(agents, interactions)

#         # 📌 Verificar si la política de vacunación está activa y continuar vacunando progresivamente
#         if self.active_policies.get(VaccinationPolicy, False):
#             for policy in self.policies:
#                 if isinstance(policy, VaccinationPolicy):
#                     total_vaccination = policy.enforce(agents, clusters)  # Continúa vacunando
#                     if total_vaccination :
#                         self.remove_policies(agents,clusters, VaccinationPolicy)
                        
#         self.evaluate_policies(agents, clusters, day)
