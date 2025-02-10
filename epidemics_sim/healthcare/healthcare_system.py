import random
from epidemics_sim.healthcare.deep2 import SimulationAnalyzer
from epidemics_sim.policies.vaccination_policy import VaccinationPolicy
from epidemics_sim.policies.lockdown_policy import LockdownPolicy
from epidemics_sim.policies.mask_policy import MaskUsagePolicy
from epidemics_sim.policies.social_distancing_policy import SocialDistancingPolicy
from epidemics_sim.agents.base_agent import State

class HealthcareSystem:
    def __init__(self, hospital_capacity, isolation_capacity, policies=[], demografics = {}):
        self.hospital_capacity = hospital_capacity
        self.isolation_capacity = isolation_capacity
        self.hospitalized = []
        self.isolated = []
        self.analyzer = SimulationAnalyzer()
        self.policies = policies
        self.active_policies = {policy: False for policy in self.policies}
        self.policy_counters = {policy: 0 for policy in self.policies}
        self.days_since_last_evaluation = 0
        self.daily_cases = []  # Para almacenar los casos diarios
        self.daily_deaths = []  # Para almacenar las muertes diarias
        self.municipality_data = {mun : 0 for mun in demografics.keys()} 

    def monitor_health_status(self, agents, interactions):
        # new_cases = sum(1 for agent in agents if agent.infection_status["state"] == State.INFECTED)
        # new_deaths = sum(1 for agent in agents if agent.infection_status["state"] == State.DECEASED)
        new_cases = 0
        new_deaths = 0

        # Calcular casos por municipio
        for agent in agents:
            if agent.infection_status["state"] == State.INFECTED:
                new_cases += 1
                municipio = agent.municipio
                if municipio == "PLAYA":
                    g=7
                
                if municipio not in self.municipality_data:
                    self.municipality_data[municipio] = 0
                self.municipality_data[municipio] += 1
            elif agent.infection_status["state"] == State.DECEASED:
                new_deaths += 1
        self.analyzer.record_daily_stats(new_cases, new_deaths, self.municipality_data)
        
        self.daily_cases.append(new_cases)
        self.daily_deaths.append(new_deaths)
        
        if len(self.daily_cases) > 10:
            self.daily_cases.pop(0)
        if len(self.daily_deaths) > 10:
            self.daily_deaths.pop(0)
        
        self.hospitalized = [a for a in self.hospitalized if a.infection_status["state"] not in [State.RECOVERED, State.DECEASED]]
        self.isolated = [a for a in self.isolated if a.infection_status["state"] not in [State.RECOVERED, State.DECEASED]]
        
        prioritized_cases = sorted(
            [a for a in agents if a.infection_status["severity"] in ["mild", "moderate", "severe", "critical"] and not a.is_hospitalized and not a.is_isolated],
            key=lambda x: ["critical", "severe", "moderate", "mild"].index(x.infection_status["severity"])
        )

        for agent in prioritized_cases:
            if len(self.hospitalized) < self.hospital_capacity:
                self.hospitalized.append(agent)
                agent.is_hospitalized, agent.is_isolated = True, False
            elif len(self.isolated) < self.isolation_capacity:
                self.isolated.append(agent)
                agent.is_isolated, agent.is_hospitalized = True, False

    def evaluate_policies(self, agents, clusters, day):
        if self.days_since_last_evaluation < 10:
            self.days_since_last_evaluation += 1
            return

        self.days_since_last_evaluation = 0
        total_population = len(agents)
        total_infected = sum(1 for agent in agents if agent.infection_status["state"] == State.INFECTED)
        infection_rate = total_infected / total_population if total_population > 0 else 0
        hospital_occupancy = len(self.hospitalized) / self.hospital_capacity
        
        avg_cases_last_10_days = sum(self.daily_cases) / len(self.daily_cases) if self.daily_cases else 0
        avg_deaths_last_10_days = sum(self.daily_deaths) / len(self.daily_deaths) if self.daily_deaths else 0
        
        print("\n📊 Evaluación de la situación epidemiológica (Día", day, ")")
        print("Tasa de infección actual: {:.2%}".format(infection_rate))
        print("Ocupación hospitalaria: {:.2%}".format(hospital_occupancy))
        print("Promedio de casos diarios en los últimos 10 días: {:.2f}".format(avg_cases_last_10_days))
        print("Promedio de muertes diarias en los últimos 10 días: {:.2f}".format(avg_deaths_last_10_days))
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
        for policy in self.policies:
            if isinstance(policy, policy_type):
                policy.enforce(agents, clusters)
                self.active_policies[policy_type] = True
                print(f"✅ {policy_type.__name__} aplicada.")

    def remove_policies(self, agents, clusters, policy_type):
        for policy in self.policies:
            if isinstance(policy, policy_type):
                policy.delete(agents, clusters)
                self.active_policies[policy_type] = False
                print(f"🛑 {policy_type.__name__} eliminada.")

    def daily_operations(self, agents, clusters, interactions, day):
        self.monitor_health_status(agents, interactions)
        # 📌 Verificar si la política de vacunación está activa y continuar vacunando progresivamente
        if self.active_policies.get(VaccinationPolicy, False):
            for policy in self.policies:
                if isinstance(policy, VaccinationPolicy):
                    total_vaccination = policy.enforce(agents, clusters)  # Continúa vacunando
                    if total_vaccination :
                        self.remove_policies(agents,clusters, VaccinationPolicy)
        self.evaluate_policies(agents, clusters, day)
