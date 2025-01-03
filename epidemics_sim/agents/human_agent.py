from epidemics_sim.agents.base_agent import BaseAgent
from epidemics_sim.agents.base_agent import State

class HumanAgent(BaseAgent):
    def __init__(
        self, agent_id, age, gender, occupation, household_id, infection_status,
        comorbidities=[], attributes={},initial_state=State.SUSCEPTIBLE
    ):
        """
        Represents a human agent with attributes relevant for epidemic simulations.

        :param agent_id: Unique identifier for the agent.
        :param initial_state: Initial state of the agent (e.g., SUSCEPTIBLE).
        :param age: Age of the agent.
        :param gender: Gender of the agent (e.g., 'male', 'female', 'other').
        :param occupation: Occupation of the agent (e.g., 'student', 'worker', 'retired').
        :param household_id: ID of the household the agent belongs to.
        :param comorbidities: List of comorbidities (optional).
        :param infection_status: Current infection details (optional, e.g., 'asymptomatic', 'severe').
        :param attributes: Additional attributes (optional).
        """
        super().__init__(agent_id, initial_state, attributes)
        self.age = age
        self.gender = gender
        self.occupation = occupation
        self.household_id = household_id
        self.comorbidities = comorbidities or []
        self.infection_status = infection_status

    @property
    def is_infected(self):
        """
        Determine if the agent is infected based on the infection status.
        """
        return self.infection_status == State.INFECTED
    
    @property
    def is_recovered(self):
        """
        Determine if the agent is recovered based on the infection status.
        """
        return self.infection_status == State.RECOVERED
    
    @property
    def is_deceased(self):
        """
        Determine if the agent is deceased based on the infection status.
        """
        return self.infection_status == State.DECEASED  
    
    @property
    def medical_age(self):
        """
        Determine the medical age of the agent based on age and comorbidities.
        """
        return self.age + 5*len(self.comorbidities)
    
    def is_high_risk(self):
        """
        Determine if the agent is high-risk based on age and comorbidities.
        """
        high_risk_conditions = ["diabetes", "hypertension", "obesity", "asthma"]
        return self.age > 65 or any(c in high_risk_conditions for c in self.comorbidities)

    def __repr__(self):
        return (
            f"HumanAgent(id={self.agent_id}, state={self.state}, age={self.age}, "
            f"gender={self.gender}, occupation={self.occupation}, household_id={self.household_id}, "
            f"comorbidities={self.comorbidities}, infection_status={self.infection_status}, "
            f"attributes={self.attributes})"
        )
