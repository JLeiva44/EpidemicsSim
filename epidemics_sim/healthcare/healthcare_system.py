from epidemics_sim.healthcare.dashboard import CovidDashboard
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
        self.analyzer = CovidDashboard()
        self.policies = policies
        if len(policies )> 0:
            self.active_policies = { policy:False for policy in self.policies}
        
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
        if len(self.policies) > 0:
            self.analyze_and_apply_policies(agents, clusters, day)

