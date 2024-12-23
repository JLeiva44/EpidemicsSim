from epidemics_sim.environments.base_environment import BaseEnvironment

class City(BaseEnvironment):
    def __init__(self, env_id, name, population, dimensions, attributes=None):
        """
        Represents a city environment with specific attributes.

        :param env_id: Unique identifier for the city.
        :param name: Name of the city.
        :param population: Total population of the city.
        :param dimensions: Tuple representing the dimensions of the city.
        :param attributes: Dictionary of additional attributes for the city.
        """
        super().__init__(env_id, name, dimensions, attributes)
        self.population = population

    def distribute_agents(self, agents):
        """
        Distribute agents across the city.

        :param agents: List of agents to distribute.
        """
        self.agents = agents

    def __repr__(self):
        return (
            f"City(id={self.env_id}, name={self.name}, population={self.population}, "
            f"dimensions={self.dimensions}, num_agents={len(self.agents)}, attributes={self.attributes})"
        )
