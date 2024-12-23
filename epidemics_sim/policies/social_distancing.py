from epidemics_sim.policies.base_policy import BasePolicy

class SocialDistancing(BasePolicy):
    def __init__(self, reduction_factor):
        """
        Specific implementation of a social distancing policy.

        :param reduction_factor: Factor by which interactions are reduced (0 to 1).
        """
        super().__init__(
            name="Social Distancing",
            description="Reduce the frequency of interactions between agents."
        )
        self.reduction_factor = reduction_factor

    def apply(self, environment):
        """
        Apply social distancing by reducing interaction probabilities.

        :param environment: An instance of BaseEnvironment or its subclasses.
        """
        for agent in environment.agents:
            agent.attributes["interaction_reduction"] = self.reduction_factor
        print(f"Social distancing applied to environment {environment.name} with reduction factor {self.reduction_factor}.")
