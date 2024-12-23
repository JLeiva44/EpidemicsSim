from epidemics_sim.policies.base_policy import BasePolicy
class Lockdown(BasePolicy):
    def __init__(self):
        """
        Specific implementation of a lockdown policy.
        """
        super().__init__(
            name="Lockdown",
            description="Restrict movement of agents to reduce interactions."
        )

    def apply(self, environment):
        """
        Apply lockdown by restricting agent movements in the environment.

        :param environment: An instance of BaseEnvironment or its subclasses.
        """
        for agent in environment.agents:
            agent.attributes["movement_restricted"] = True
        print(f"Lockdown applied to environment {environment.name}.")
