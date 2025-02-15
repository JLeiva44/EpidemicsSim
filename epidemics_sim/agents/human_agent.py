from epidemics_sim.agents.base_agent import BaseAgent
from epidemics_sim.agents.base_agent import State
import random
import math
class HumanAgent(BaseAgent):
    def __init__(
        self, agent_id, age, gender, occupation, household_id, municipio, disease_model,
    comorbidities=[]
    ):
        """
        Represents a human agent with attributes relevant for epidemic simulations.

        :param agent_id: Unique identifier for the agent.
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
        super().__init__(agent_id)
        self.age = age
        self.gender = gender
        self.occupation = occupation
        self.household_id = household_id
        self.household = []
        self.municipio = municipio
        self.comorbidities = comorbidities or []
        #self.infection_status = infection_status
        self.days_infected = 0  # Days since infection (reset upon recovery)
        self.vaccinated = False
        self.initial = False
        self.vaccine_effectiveness = None
        self.mask ={
            "usage":False,
            "reduction_factor" : 1
        } 
        self.immune = False
        self.is_isolated = False
        self.is_hospitalized = False
        self.asymtomathic = None
        self.mortality_rate = self._calculate_base_mortality_rate()
        self.disease_model = disease_model
        self.incubation_period = 0

        self.infection_status ={
                "disease": "",
                "state": State.SUSCEPTIBLE,
                "severity": None,
                "contagious": None,  # Not contagious during incubation
                "days_infected": 0,
                "asymptomatic": None,
                "immunity_days": 0,
                "diagnosis_delay" : 0
            }


    import math

    def _calculate_base_mortality_rate(self):
            """
            Calculate the agent's base mortality rate based on their biological age,
            following an exponential growth model.

            Biological age is estimated as:
                biological_age = age + 5 * (# of comorbidities)
            
            Base mortality rate is modeled as an exponential function:
                base_mortality_rate = 10^(-5) * e^((biological_age - 30) / 20)
            
            This ensures a gradual increase in mortality rather than discrete jumps.

            :return: Base mortality rate as a decimal.
            """
            biological_age = self.age + 5 * len(self.comorbidities)

            # Exponential function to model mortality increase
            base_mortality_rate = max(0, 0.001 * (biological_age - 30))  #= 1e-5 * math.exp((biological_age - 30) / 20)


            # Cap the mortality rate at a realistic max (e.g., 20% for extreme ages)
            return  base_mortality_rate#min(base_mortality_rate, 0.2)

    # def _calculate_base_mortality_rate(self):
    #     """
    #     Calculate the agent's base mortality rate based on their biological age.

    #     Biological age is defined as:
    #     biological_age = historical_age + 5 * (# of comorbidities)

    #     The base mortality rate is then derived from this biological age:
    #     - 0-30 years: 0.01%
    #     - 31-50 years: 0.1%
    #     - 51-70 years: 1%
    #     - 71+ years: 5%

    #     :return: Base mortality rate as a decimal.
    #     """
    #     biological_age = self.age + 5 * len(self.comorbidities)
    #     if biological_age <= 30:
    #         return 0.00001  # 0.001%
    #     elif biological_age <= 50:
    #         return 0.0001   # 0.01%
    #     elif biological_age <= 70:
    #         return 0.001    # 0.1%
    #     else:
    #         return 0.01 # 1%

    

    def reset_agent(self):
        """
        Reset the agent to a susceptible state after recovery.

        :param agent: The recovered agent.
        """
        self.reset_infection()

    def enforce_policies(self, policies):
        pass
    
    def enforce_isolation(self, days):
        """
        Enforce isolation rules on an agent, preventing state progression.

        :param agent: The agent to isolate.
        :param days: Number of days the agent will be isolated.
        """
        self.is_isolated = True
        self.isolation_days = days

    def manage_vaccination(self,efficacy):
        """
        Manage vaccination effects on an agent.

        :param agent: The agent being vaccinated.
        :param efficacy: Efficacy of the vaccine in reducing transmission/severity.
        """
        if random.random() < efficacy:
            self.immune = True
            self.transition(State.RECOVERED_IMMUNE, reason="Vaccination")

    def release_isolation(self):
        """
        Release an agent from isolation once the period ends.

        :param agent: The agent to release.
        """
        if self.isolated:
            self.isolation_days -= 1
            if self.isolation_days <= 0:
                self.isolated = False
                self.isolation_days = 0

    def __eq__(self, value):
        return self.agent_id == value.agent_id

    def __repr__(self):
        return (
            f"HumanAgent(id={self.agent_id}, state={self.infection_status['state']}, age={self.age}, "
            f"gender={self.gender}, occupation={self.occupation}, household_id={self.household_id}, "
            f"municipio={self.municipio}, consultorio={self.consultorio}, policlinico={self.policlinico}, "
            f"comorbidities={self.comorbidities}, severity={self.infection_status['severity']}, "
            f"immune={self.immune})"
        )


# Example functions for severity and recovery
