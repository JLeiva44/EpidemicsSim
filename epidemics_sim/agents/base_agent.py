



class BaseAgent:
    def __init__(self, agent_id):
        """
        Base class for an agent in the simulation.

        :param agent_id: Unique identifier for the agent.
        :param initial_state: Initial state of the agent (e.g., SUSCEPTIBLE).
        :param attributes: Dictionary of additional attributes for the agent.
        """
        self.agent_id = agent_id
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
