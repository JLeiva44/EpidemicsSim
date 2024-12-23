from .base_disease import BaseDisease
class Covid(BaseDisease):
    def __init__(self):
        """
        Specific implementation for the COVID-19 disease.
        """
        super().__init__(
            name="COVID-19",
            transmission_rate=0.03,  # Example value
            recovery_rate=0.01,      # Example value
            mortality_rate=0.005     # Example value
        )

    def __repr__(self):
        return f"Covid(name={self.name}, transmission_rate={self.transmission_rate}, recovery_rate={self.recovery_rate}, mortality_rate={self.mortality_rate})"
