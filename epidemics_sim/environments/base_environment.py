class BaseEnvironment:
    def __init__(self, env_id, name, dimensions, attributes=None):
        """
        Base class for an environment in the simulation.

        :param env_id: Unique identifier for the environment.
        :param name: Name of the environment.
        :param dimensions: Tuple representing the dimensions of the environment (e.g., (width, height)).
        :param attributes: Dictionary of additional attributes for the environment.
        """
        self.env_id = env_id
        self.name = name
        self.dimensions = dimensions
        self.attributes = attributes or {}
        self.agents = []  # List of agents in the environment

    def add_agent(self, agent):
        """
        Add an agent to the environment.

        :param agent: An instance of BaseAgent or its subclasses.
        """
        self.agents.append(agent)

    def remove_agent(self, agent):
        """
        Remove an agent from the environment.

        :param agent: An instance of BaseAgent or its subclasses.
        """
        self.agents.remove(agent)

    def __repr__(self):
        return (
            f"BaseEnvironment(id={self.env_id}, name={self.name}, dimensions={self.dimensions}, "
            f"num_agents={len(self.agents)}, attributes={self.attributes})"
        )