class BaseDisease:
    def __init__(self, name, transmission_rate, recovery_rate, mortality_rate):
        """
        Base class for diseases in the simulation.

        :param name: Name of the disease.
        :param transmission_rate: Probability of disease transmission per interaction.
        :param recovery_rate: Probability of recovery per time step.
        :param mortality_rate: Probability of death per time step for infected agents.
        """
        self.name = name
        self.transmission_rate = transmission_rate
        self.recovery_rate = recovery_rate
        self.mortality_rate = mortality_rate

    def __repr__(self):
        return (
            f"BaseDisease(name={self.name}, transmission_rate={self.transmission_rate}, "
            f"recovery_rate={self.recovery_rate}, mortality_rate={self.mortality_rate})"
        )
