from epidemics_sim.agents.base_agent import BaseAgent
from epidemics_sim.agents.base_agent import State

class HumanAgent(BaseAgent):
    def __init__(
        self, agent_id, age, gender, occupation, household_id, municipio,
        infection_status=None, comorbidities=[], attributes={},
        initial_state=State.SUSCEPTIBLE, consultorio=None, policlinico=None
    ):
        """
        Represents a human agent with attributes relevant for epidemic simulations.

        :param agent_id: Unique identifier for the agent.
        :param initial_state: Initial state of the agent (e.g., SUSCEPTIBLE).
        :param age: Age of the agent.
        :param gender: Gender of the agent (e.g., 'male', 'female', 'other').
        :param occupation: Occupation of the agent (e.g., 'student', 'worker', 'retired').
        :param household_id: ID of the household the agent belongs to.
        :param municipio: The municipality the agent belongs to.
        :param infection_status: Current infection details (optional, e.g., 'asymptomatic', 'severe').
        :param comorbidities: List of comorbidities (optional).
        :param attributes: Additional attributes (optional).
        :param consultorio: Assigned consultorio (primary healthcare unit).
        :param policlinico: Assigned policlínico (secondary healthcare unit).
        """
        super().__init__(agent_id, initial_state, attributes)
        self.age = age
        self.gender = gender
        self.occupation = occupation
        self.household_id = household_id
        self.municipio = municipio
        self.comorbidities = comorbidities or []
        self.infection_status = infection_status or {"state": initial_state, "severity": None}
        self.days_infected = 0  # Days since infection (reset upon recovery)
        self.vaccinated = False
        self.mask_usage = False
        self.immune = False
        self.consultorio = consultorio
        self.policlinico = policlinico

    @property
    def is_infected(self):
        return self.infection_status["state"] == State.INFECTED

    @property
    def is_critical(self):
        return self.infection_status["state"] == "critical"

    @property
    def is_recovered(self):
        return self.infection_status["state"] == State.RECOVERED

    @property
    def is_deceased(self):
        return self.infection_status["state"] == State.DECEASED

    def progress_infection(self, severity_func, mortality_rate):
        """
        Progress the infection state for this agent.

        :param severity_func: Function to determine severity of the infection.
        :param mortality_rate: Probability of death if in critical condition.
        """
        if self.is_infected:
            self.days_infected += 1

            if self.days_infected == 5:
                # Determine severity after 5 days
                self.infection_status["severity"] = severity_func()
                if self.infection_status["severity"] in ["severe", "critical"]:
                    self.infection_status["state"] = "critical"

            elif self.days_infected == 10:
                # Recovery or death after 10 days
                if self.is_critical and random.random() < mortality_rate:
                    self.infection_status["state"] = State.DECEASED
                else:
                    self.infection_status["state"] = State.RECOVERED
                    self.immune = True

    def reset_infection(self):
        """
        Reset infection-related attributes upon recovery.
        """
        self.infection_status = {"state": State.SUSCEPTIBLE, "severity": None}
        self.days_infected = 0

    def __repr__(self):
        return (
            f"HumanAgent(id={self.agent_id}, state={self.infection_status['state']}, age={self.age}, "
            f"gender={self.gender}, occupation={self.occupation}, household_id={self.household_id}, "
            f"municipio={self.municipio}, consultorio={self.consultorio}, policlinico={self.policlinico}, "
            f"comorbidities={self.comorbidities}, severity={self.infection_status['severity']}, "
            f"immune={self.immune})"
        )
