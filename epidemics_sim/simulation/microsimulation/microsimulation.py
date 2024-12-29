from epidemics_sim.simulation.simulation import Simulation

class Microsimulation(Simulation):
    def __init__(self, state, agents, environment):
        """
        Microsimulation class extending the main Simulation class.

        :param state: An instance of SimulationState.
        :param agents: List of agents in the simulation.
        :param environment: The environment in which the simulation takes place.
        """
        super().__init__(state, agents, environment)
        self.households = []

    def initialize_households(self, household_sizes):
        """
        Create households based on the provided sizes.

        :param household_sizes: List of integers representing household sizes.
        """
        for i, size in enumerate(household_sizes):
            household = {
                "id": i,
                "members": self.agents[:size]
            }
            self.households.append(household)
            self.agents = self.agents[size:]

    def assign_roles(self):
        """
        Assign roles (e.g., worker, student) to agents based on age or other attributes.
        """
        for household in self.households:
            for agent in household["members"]:
                age = agent.attributes.get("age", 0)
                if age < 18:
                    agent.attributes["role"] = "student"
                elif age < 65:
                    agent.attributes["role"] = "worker"
                else:
                    agent.attributes["role"] = "retired"

    def step(self):
        """
        Perform a single step in the microsimulation.
        """
        print(f"Step {self.state.time_step}: Starting microsimulation step.")

        for agent in self.agents:
            if agent.state == "INFECTED":
                agent.transition("DIAGNOSED", reason="Detected during interaction")
                self.state.update_agent_state(agent.agent_id, agent.state)

        self.state.increment_time()

    def run(self, steps):
        """
        Run the microsimulation for a given number of steps.

        :param steps: Number of steps to simulate.
        """
        print("Initializing households and roles...")
        self.initialize_households([4, 3, 5])  # Example sizes
        self.assign_roles()

        for _ in range(steps):
            self.step()