import random
from epidemics_sim.agents.base_agent import State

def progress_infection(self, agent):
    """
    Progress the infection state for the given agent.

    :param agent: The agent whose infection state is being progressed.
    """
    if agent.infection_status["days_infected"] == 0:
        agent.incubation_period = self.incubation_period()

    agent.infection_status["days_infected"] += 1
    days_infected = agent.infection_status["days_infected"]

    # 1️⃣ INCUBACIÓN: No síntomas ni transmisión hasta que termine
    if days_infected <= agent.incubation_period:
        agent.infection_status["contagious"] = False
        return

    # 2️⃣ FIN DE INCUBACIÓN: Definir severidad y contagiosidad
    if days_infected == agent.incubation_period + 1:
        agent.infection_status["contagious"] = True  # Ahora puede contagiar
        if agent.infection_status["asymptomatic"]:
            agent.infection_status.update({
                "severity": "asymptomatic",
                "state": State.INFECTED
            })
            agent.transition(State.INFECTED, reason=f"{self.name} infection")
        else:
            severity = self.determine_severity(agent)
            agent.infection_status.update({
                "severity": severity,
                "state": State.INFECTED
            })
            agent.transition(State.INFECTED, reason=f"{self.name} infection ({severity})")
        return

    # 3️⃣ PROGRESIÓN: Evaluar cambio de gravedad
    severity = agent.infection_status.get("severity", "mild")
    recovery_days = self.severity_durations.get(severity, 10)  # Tiempo base de recuperación

    # 💡 Bonus de recuperación si está hospitalizado
    recovery_bonus = 1.3 if agent.is_hospitalized else 1.0  

    # Posibilidades de que la enfermedad empeore
    progression_rates = {
        "mild": 0.15,        # 15% de pasar a moderado
        "moderate": 0.25,    # 25% de pasar a severo
        "severe": 0.40,      # 40% de pasar a crítico
    }

    # Evaluar si el paciente empeora
    if severity in progression_rates and random.random() < progression_rates[severity]:
        new_severity = {
            "mild": "moderate",
            "moderate": "severe",
            "severe": "critical"
        }[severity]
        agent.infection_status.update({"severity": new_severity})
        agent.transition(State.INFECTED, reason=f"{self.name} worsened to {new_severity}")
        return

    # 4️⃣ Evaluar recuperación o muerte
    if days_infected >= agent.incubation_period + recovery_days:
        # 🚨 CASOS CRÍTICOS: Posibilidad de muerte
        if severity == "critical" and random.random() < (agent.update_mortality_rate(self.base_mortality_rate) / recovery_bonus):
            agent.infection_status.update({
                "state": State.DECEASED,
                "contagious": False,
                "severity": "critical"
            })
            agent.transition(State.DECEASED, reason=f"{self.name} critical condition")
            return  # 🚨 Agente murió, no sigue en la simulación

        # ✅ RECUPERACIÓN: Puede ser inmune o volver a ser susceptible
        if random.random() < (self.recovery_rates.get(severity, 1.0) * recovery_bonus):
            agent.infection_status.update({
                "state": State.RECOVERED,
                "contagious": False,
                "severity": None,
                "days_infected": 0,
            })
            agent.transition(State.RECOVERED, reason=f"{self.name} recovery")

            # 3.3️⃣ ¿La inmunidad es temporal?
            if self.immunity_duration > 0:
                agent.infection_status["immunity_days"] = self.immunity_duration
            else:
                agent.infection_status["immunity_days"] = 0
            return

    # 5️⃣ REINFECCIÓN: Si la inmunidad es temporal, vuelve a ser susceptible
    if agent.infection_status["state"] == State.RECOVERED and "immunity_days" in agent.infection_status:
        agent.infection_status["immunity_days"] -= 1
        if agent.infection_status["immunity_days"] <= 0:
            agent.infection_status.update({
                "state": State.SUSCEPTIBLE,
                "disease": "",
                "severity": None,
                "contagious": False,
                "days_infected": 0,
                "asymptomatic": None,
                "immunity_days": 0
            })
            agent.transition(State.SUSCEPTIBLE, reason=f"{self.name} immunity waned")
            agent.immune = False  
