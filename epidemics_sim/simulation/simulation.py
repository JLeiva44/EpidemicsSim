class SimulationState:
    def __init__(self):
        """
        Class to manage the state of the simulation at any given time.
        """
        self.time_step = 0
        self.agent_states = {}
        self.environment_states = {}

    def update_agent_state(self, agent_id, new_state):
        """
        Update the state of a specific agent.

        :param agent_id: Unique identifier of the agent.
        :param new_state: New state of the agent.
        """
        self.agent_states[agent_id] = new_state

    def update_environment_state(self, environment_id, new_state):
        """
        Update the state of a specific environment.

        :param environment_id: Unique identifier of the environment.
        :param new_state: New state of the environment.
        """
        self.environment_states[environment_id] = new_state

    def increment_time(self):
        """
        Advance the simulation by one time step.
        """
        self.time_step += 1

    def __repr__(self):
        return (
            f"SimulationState(time_step={self.time_step}, agent_states={len(self.agent_states)}, "
            f"environment_states={len(self.environment_states)})"
        )


class Simulation:
    def __init__(self, state, agents, environment):
        """
        Main simulation class.

        :param state: An instance of SimulationState.
        :param agents: List of agents in the simulation.
        :param environment: The environment in which the simulation takes place.
        """
        self.state = state
        self.agents = agents
        self.environment = environment

    def step(self):
        """
        Perform a single simulation step.
        """
        # Example logic: Update states and interactions
        for agent in self.agents:
            if agent.state == "INFECTED":
                agent.transition("RECOVERED", reason="Natural recovery")
                self.state.update_agent_state(agent.agent_id, agent.state)

        self.state.increment_time()
        print(f"Time step {self.state.time_step} completed.")

    def run(self, steps):
        """
        Run the simulation for a given number of steps.

        :param steps: Number of steps to simulate.
        """
        for _ in range(steps):
            self.step()

    def __repr__(self):
        return f"Simulation(state={self.state}, num_agents={len(self.agents)})"
