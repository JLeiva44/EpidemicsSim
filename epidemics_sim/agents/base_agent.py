

from enum import Enum

class State(Enum):
    SUSCEPTIBLE = 0
    INFECTED = 1
    RECOVERED = 2
    DECEASED = 3
    DIAGNOSED = 4
    ASYMPTOMATIC = 5
    SYMPTOMATIC = 6
    SEVERE = 7
    CRITICAL = 8
    RECOVERED_IMMUNE = 9



class BaseAgent:
    def __init__(self, agent_id, initial_state = State.SUSCEPTIBLE, attributes=None):
        """
        Base class for an agent in the simulation.

        :param agent_id: Unique identifier for the agent.
        :param initial_state: Initial state of the agent (e.g., SUSCEPTIBLE).
        :param attributes: Dictionary of additional attributes for the agent.
        """
        self.agent_id = agent_id
        self.state = initial_state
        self.attributes = attributes or {}
        self.history = []  # Records state transitions for analysis

    def transition(self, new_state, reason=None):
        """
        Transition the agent to a new state and log the change.

        :param new_state: The new state of the agent.
        :param reason: Reason for the state transition (optional).
        """
        self.history.append((self.state, new_state, reason))
        self.state = new_state

    def __repr__(self):
        return f"BaseAgent(id={self.agent_id}, state={self.state}, attributes={self.attributes})"
