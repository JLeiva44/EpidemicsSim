class BasePolicy:
    def __init__(self, name, description):
        """
        Base class for policies applied during the simulation.

        :param name: Name of the policy.
        :param description: Brief description of the policy.
        """
        self.name = name
        self.description = description

    def apply(self, environment):
        """
        Apply the policy to the given environment.

        :param environment: An instance of BaseEnvironment or its subclasses.
        """
        raise NotImplementedError("This method should be overridden by subclasses.")

    def __repr__(self):
        return f"BasePolicy(name={self.name}, description={self.description})"
