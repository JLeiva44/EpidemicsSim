from .base_disease import BaseDisease
class Dengue(BaseDisease):
    def __init__(self):
        """
        Specific implementation for the Dengue disease.
        """
        super().__init__(
            name="Dengue",
            transmission_rate=0.02,  # Example value
            recovery_rate=0.015,     # Example value
            mortality_rate=0.002     # Example value
        )

    def __repr__(self):
        return f"Dengue(name={self.name}, transmission_rate={self.transmission_rate}, recovery_rate={self.recovery_rate}, mortality_rate={self.mortality_rate})"
