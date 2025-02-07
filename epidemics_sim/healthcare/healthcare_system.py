from epidemics_sim.healthcare.utils import SimulationAnalyzer
from epidemics_sim.policies.vaccination_policy import VaccinationPolicy
from epidemics_sim.policies.lockdown_policy import LockdownPolicy
from epidemics_sim.agents.base_agent import State
import random

class HealthcareSystem:
    def __init__(self, hospital_capacity, isolation_capacity, policies=[]):
        self.hospital_capacity = hospital_capacity
        self.isolation_capacity = isolation_capacity
        self.hospitalized = []
        self.isolated = []
        self.analyzer = SimulationAnalyzer()
        self.policies = policies
        self.active_policies = {
            LockdownPolicy: False,
            VaccinationPolicy: False
        }
        self.policy_counters = {
            "lockdown": 0  # Contador para estabilidad de cuarentena
        }

    def monitor_health_status(self, agents, interactions):
        self.analyzer.record_daily_stats(agents, interactions, len(self.hospitalized), len(self.isolated))  

        self.hospitalized = [a for a in self.hospitalized if a.infection_status["state"] not in [State.RECOVERED, State.DECEASED]]
        self.isolated = [a for a in self.isolated if a.infection_status["state"] not in [State.RECOVERED, State.DECEASED]]

        severe_cases = [a for a in agents if a.infection_status["severity"] == "severe" and not a.is_hospitalized and not a.is_isolated]
        critical_cases = [a for a in agents if a.infection_status["severity"] == "critical" and not a.is_hospitalized]

        for agent in critical_cases + severe_cases:
            if len(self.hospitalized) < self.hospital_capacity:
                self.hospitalized.append(agent)
                agent.is_hospitalized, agent.is_isolated = True, False
            elif len(self.isolated) < self.isolation_capacity:
                self.isolated.append(agent)
                agent.is_isolated, agent.is_hospitalized = True, False

    def enforce_policies(self, agents, clusters, day, policy_type):
        if not self.active_policies[policy_type]:
            for policy in self.policies:
                if isinstance(policy, policy_type):
                    policy.enforce(agents, clusters)
                    self.active_policies[policy_type] = True
                    print(f"✅ {policy_type.__name__} applied.")
        
        active_policy_names = [p.__name__ for p, active in self.active_policies.items() if active]
        self.analyzer.record_policy(day, active_policy_names)

    def remove_policies(self, agents, clusters, policy_type):
        if self.active_policies[policy_type]:
            for policy in self.policies:
                if isinstance(policy, policy_type):
                    policy.delete(agents, clusters)
                    self.active_policies[policy_type] = False
                    print(f"🛑 {policy_type.__name__} lifted.")

    def analyze_and_apply_policies(self, agents, clusters, day):
        total_population = len(agents)
        total_infected = sum(1 for agent in agents if agent.infection_status["state"] == State.INFECTED)
        infection_rate = total_infected / total_population if total_population > 0 else 0
        hospital_occupancy = len(self.hospitalized) / self.hospital_capacity

        if self.active_policies[LockdownPolicy]:
            self.policy_counters["lockdown"] += 1
        # 🔹 Aplicación de cuarentena con umbrales mejorados
        if infection_rate > 0.12 and not self.active_policies[LockdownPolicy]:
            print("🚨 Infection rate > 12%! Enforcing lockdown.")
            self.enforce_policies(agents, clusters, day, LockdownPolicy)
            self.policy_counters["lockdown"] = 0  # Reiniciar el contador
        elif infection_rate < 0.04 and self.active_policies[LockdownPolicy]:
            #self.policy_counters["lockdown"] += 1
            if self.policy_counters["lockdown"] >= 10 :  # Esperar 3 días
                print("✅ Infection rate < 4% for 10 days! Removing lockdown.")
                self.remove_policies(agents, clusters, LockdownPolicy)

        # 🔹 Reglas para hospitalización
        elif hospital_occupancy > 0.9 and not self.active_policies[LockdownPolicy]:
            print("⚠️ Hospital capacity critical! Enforcing lockdown.")
            self.enforce_policies(agents, clusters, day, LockdownPolicy)
            self.policy_counters["lockdown"] = 0
        elif hospital_occupancy < 0.4 and self.active_policies[LockdownPolicy]:
            #self.policy_counters["lockdown"] += 1
            if self.policy_counters["lockdown"] >= 8 :
                print("✅ Hospital capacity < 40% for 8 days! Removing lockdown.")
                self.remove_policies(agents, clusters, LockdownPolicy)
        
        # 🔹 Aplicar vacunación si está disponible
        if not self.active_policies[VaccinationPolicy]:
            print("💉 Applying vaccination policy.")
            self.enforce_policies(agents, clusters, day, VaccinationPolicy)

    def daily_operations(self, agents, clusters, interactions, day):
        self.monitor_health_status(agents, interactions)
        self.analyze_and_apply_policies(agents, clusters, day)

# from epidemics_sim.healthcare.utils import SimulationAnalyzer
# from epidemics_sim.policies.vaccination_policy import VaccinationPolicy
# from epidemics_sim.policies.lockdown_policy import LockdownPolicy
# from epidemics_sim.agents.base_agent import State
# import random

# class HealthcareSystem:
#     def __init__(self, hospital_capacity, isolation_capacity, policies=[]):
#         """
#         Central healthcare system to monitor infections and manage responses.

#         :param hospital_capacity: Number of available hospital beds.
#         :param isolation_capacity: Number of available isolation spaces.
#         :param policies: List of available policies (lockdowns, vaccinations, etc.).
#         """
#         self.hospital_capacity = hospital_capacity
#         self.isolation_capacity = isolation_capacity
#         self.hospitalized = []
#         self.isolated = []
#         self.analyzer = SimulationAnalyzer()
#         self.policies = policies
#         self.active_policies = {
#             LockdownPolicy : False
#         }  # 🔥 Diccionario para rastrear políticas activas

#     def monitor_health_status(self, agents, interactions):
#         """
#         Monitor the health status of all agents and manage hospitalization/isolation.

#         :param agents: List of agents in the simulation.
#         """
#         # 📌 Registrar estadísticas antes de modificar listas
#         self.analyzer.record_daily_stats(agents,interactions, len(self.hospitalized), len(self.isolated))  

#         # 1️⃣ Remover agentes recuperados o fallecidos de hospitales y aislamiento
#         self.hospitalized = [a for a in self.hospitalized if a.infection_status["state"] not in [State.RECOVERED, State.DECEASED]]
#         self.isolated = [a for a in self.isolated if a.infection_status["state"] not in [State.RECOVERED, State.DECEASED]]

#         # 2️⃣ Obtener agentes en estado severo o crítico que aún no están hospitalizados/aislados
#         severe_cases = [a for a in agents if a.infection_status["severity"] == "severe" and not a.is_hospitalized and not a.is_isolated]
#         critical_cases = [a for a in agents if a.infection_status["severity"] == "critical" and not a.is_hospitalized]

#         # 3️⃣ Priorizar hospitalización de casos críticos
#         for agent in critical_cases:
#             if len(self.hospitalized) < self.hospital_capacity:
#                 self.hospitalized.append(agent)
#                 agent.is_hospitalized = True
#                 agent.is_isolated = False  # 🚨 Si estaba aislado, ahora está hospitalizado
#             elif len(self.isolated) < self.isolation_capacity:
#                 self.isolated.append(agent)
#                 agent.is_isolated = True
#                 agent.is_hospitalized = False  # 🚨 Si no hay camas, al menos aislarlo

#         # 4️⃣ Hospitalizar los casos severos si hay espacio disponible
#         for agent in severe_cases:
#             if len(self.hospitalized) < self.hospital_capacity:
#                 self.hospitalized.append(agent)
#                 agent.is_hospitalized = True
#                 agent.is_isolated = False  # 🚨 Pasó de aislamiento a hospitalización si aplica
#             elif len(self.isolated) < self.isolation_capacity:
#                 self.isolated.append(agent)
#                 agent.is_isolated = True

#         # 📊 Mostrar estadísticas de ocupación hospitalaria
#         print(f"🏥 Hospitalized: {len(self.hospitalized)} / {self.hospital_capacity}")
#         print(f"🏠 Isolated: {len(self.isolated)} / {self.isolation_capacity}")

#     def enforce_policies(self, agents, clusters,day, policy_type=None):
#         """
#         Apply a specific health policy or all policies if none is specified.

#         :param agents: List of agents in the simulation.
#         :param clusters: Dictionary of clusters (work, home, etc.).
#         :param policy_type: Type of policy to apply (e.g., 'lockdown', 'vaccination').
#         """
#         if policy_type:
#             for policy in self.policies:
#                 if isinstance(policy, policy_type):
#                     # Solo aplicar si NO está activa
#                         policy.enforce(agents, clusters)
#                         self.active_policies[policy_type] = True  # 🔥 Registrar que está activa
        
#         policies = [p.__name__ for p in self.active_policies.keys() if self.active_policies[p] == True]
#         self.analyzer.record_policy(day,policies)
        
#         # else:
#         #     for policy in self.policies:
#         #         if type(policy) not in self.active_policies:
#         #             policy.enforce(agents, clusters)
#         #             self.active_policies[type(policy)] = True  # 🔥 Registrar que está activa

#     def remove_policies(self,agents, clusters, policy_type):
#         """
#         Remove an active policy when conditions improve.

#         :param policy_type: The type of policy to remove.
#         """
#         # if policy_type in self.active_policies:
#         #     self.active_policies[policy_type] = False  # 🔥 Marcar como inactiva
            
#         for policie in self.policies:
#             if isinstance(policie,policy_type):
#                 policie.delete(agents, clusters)
#                 self.active_policies[policy_type] = False
#             print(f"🛑 {policy_type.__name__} lifted.")

#     def analyze_and_apply_policies(self, agents, clusters,day):
#         """
#         Analyze the current situation and apply/remove necessary policies.

#         :param agents: List of agents in the simulation.
#         :param clusters: Dictionary of clusters.
#         """
#         total_population = len(agents)
#         total_infected = sum(1 for agent in agents if agent.infection_status["state"] == State.INFECTED)
#         infection_rate = total_infected / total_population if total_population > 0 else 0

#         # 🚨 Si más del 10% de la población está infectada, activar confinamiento
#         if infection_rate > 0.1 and self.active_policies[LockdownPolicy] == False:
#             print("🚨 High infection rate detected! Enforcing lockdown.")
#             self.enforce_policies(agents, clusters,day, LockdownPolicy)
#         # ✅ Si la tasa baja de 5%, quitar confinamiento
#         elif infection_rate < 0.05 and self.active_policies[LockdownPolicy] == True:
#             print("🚨 Bajo el rate de infeccion. Quitando el lockdown.")
#             self.remove_policies(agents, clusters, LockdownPolicy)

#         # 🏥 Si la ocupación hospitalaria es crítica (>90%), aplicar restricciones adicionales
#         elif len(self.hospitalized) / self.hospital_capacity > 0.9 and self.active_policies[LockdownPolicy] == False:
#             print("⚠️ Hospital capacity critical! Strengthening measures.")
#             self.enforce_policies(agents, clusters,day, LockdownPolicy)
#         # ✅ Si la ocupación baja del 50%, quitar restricciones adicionales
#         elif len(self.hospitalized) / self.hospital_capacity < 0.5 and self.active_policies[LockdownPolicy] == True:
#             print("⚠️ Hospital capacity Mejoro Quitando measures.")
#             self.remove_policies(agents, clusters, LockdownPolicy)

#         # Recordar poner la vacunaicon
#         # # 💉 Aplicar vacunación si está disponible
#         # self.enforce_policies(agents, clusters, VaccinationPolicy)

#     def daily_operations(self, agents, clusters, interactions,day):
#         """
#         Perform daily health system operations.

#         :param agents: List of agents in the simulation.
#         :param clusters: Dictionary of clusters.
#         """
#         self.monitor_health_status(agents, interactions)  # 📊 Registrar estadísticas primero
#         self.analyze_and_apply_policies(agents, clusters,day)  # 🛠️ Toma decisiones de salud
