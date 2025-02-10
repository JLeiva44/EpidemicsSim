import random
from epidemics_sim.policies.base_policy import Policy

class VaccinationPolicy(Policy):
    def __init__(self, vaccination_rate=0.05, vaccine_efficacy=0.8):
        """
        :param vaccination_rate: Proporción de la población a vacunar por día (ej. 0.05 = 5% diario).
        :param vaccine_efficacy: Porcentaje de reducción en la probabilidad de infección (0-1).
        """
        self.vaccination_rate = vaccination_rate
        self.vaccine_efficacy = vaccine_efficacy
        self.vaccinated_agents = set()  # 🔹 Usamos un set para llevar registro de vacunados

    def enforce(self, agents, clusters):
        """
        Aplica la vacunación progresivamente a la población.
        
        :param agents: Diccionario de agentes en la simulación.
        :param clusters: Diccionario de clusters en la simulación.
        """
        unvaccinated_agents = [agent for agent in agents.values() if not agent.vaccinated and agent.id not in self.vaccinated_agents]

        if not unvaccinated_agents:
            print("✅ Todos los agentes elegibles han sido vacunados.")
            return True # 🚨 Si ya todos están vacunados, terminamos

        num_to_vaccinate = max(1, int(len(unvaccinated_agents) * self.vaccination_rate))  # 🔹 Vacunar un % del total

        agents_to_vaccinate = random.sample(unvaccinated_agents, num_to_vaccinate)

        for agent in agents_to_vaccinate:
            agent.vaccinated = True
            agent.vaccine_effectiveness = self.vaccine_efficacy
            self.vaccinated_agents.add(agent.id)  # Registrar vacunados
            print(f"💉 Agente {agent.id} vacunado con efectividad {self.vaccine_efficacy * 100:.1f}%.")

        return False    

    def delete(self, agents, clusters):
        """
        Elimina la política de vacunación. **Nota:** No revierte las vacunas aplicadas.
        """
        print("🛑 Política de vacunación eliminada. No se administrarán más dosis.")
