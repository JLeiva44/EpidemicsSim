from city_cluster import CityClusterGenerator
from dailysim import DailySimulation
from simulation_utils import SimulationAnalyzer

class SimulationController:
    def __init__(self, demographics, config, disease_model_class, policies, simulation_days):
        """
        Initialize the simulation controller.

        :param demographics: Demographic data to generate agents.
        :param config: Configuration dictionary for the simulation.
        :param disease_model_class: Class of the disease model to use.
        :param policies: List of policy classes to apply.
        :param simulation_days: Number of days to simulate.
        """
        self.demographics = demographics
        self.config = config
        self.disease_model_class = disease_model_class
        self.policies = [policy() for policy in policies]
        self.simulation_days = simulation_days
        self.agents = self._generate_agents()
        self.cluster_generator = CityClusterGenerator(config)
        self.analyzer = SimulationAnalyzer()

    def _generate_agents(self):
        """
        Generate a synthetic population based on demographic data.

        :return: List of generated agents.
        """
        from synthetic_population import SyntheticPopulationGenerator

        generator = SyntheticPopulationGenerator(
            demographics=self.demographics
        )
        agents = generator.generate_population()
        return agents

    def run(self):
        """
        Run the simulation.

        :return: Results of the simulation.
        """
        # Generate transport interactions
        from transport_interaction import TransportInteraction

        transport_interaction = TransportInteraction(self.agents, self.config["transport"])

        # Initialize the disease model
        disease_model = self.disease_model_class(self.agents, **self.config["disease"])

        # Initialize daily simulation
        daily_simulation = DailySimulation(
            agents=self.agents,
            cluster_generator=self.cluster_generator,
            transport=transport_interaction,
            config=self.config,
            disease_model=disease_model,
            policies=self.policies
        )

        # Run simulation for the specified number of days
        simulation_results = daily_simulation.simulate(self.simulation_days)

        # Record daily statistics
        for _ in range(self.simulation_days):
            self.analyzer.record_daily_stats(self.agents)

        # Generate results
        report = self.analyzer.generate_report()
        self.analyzer.plot_statistics()

        return report

# Example configuration
example_demographics = {
    "total_population": 200,
    "age_distribution": {"0-17": 0.25, "18-64": 0.6, "65+": 0.15},
    "gender_ratio": {"male": 0.5, "female": 0.5},
    "comorbidities": {
        "diabetes": 0.1,
        "hypertension": 0.15,
        "obesity": 0.2,
        "smoking": 0.25,
        "copd": 0.05,
        "chronic_heart_disease": 0.07,
        "chronic_kidney_disease": 0.03
    }
}

example_config = {
    "home": {"duration_mean": 480, "duration_std": 120},
    "work": {"duration_mean": 480, "duration_std": 120, "min_links": 2},
    "school": {"duration_mean": 300, "duration_std": 60},
    "shopping": {"duration_mean": 37, "duration_std": 10, "max_agents": 50},
    "transport": {"interval": 5, "duration_mean": 15, "duration_std": 5},
    "household_sizes": [1, 2, 3, 4, 5, 6],
    "household_distribution": [0.1, 0.2, 0.3, 0.2, 0.15, 0.05],
    "work_sizes": [5, 10, 20, 50],
    "work_distribution": [0.4, 0.3, 0.2, 0.1],
    "school_sizes": [20, 30, 40],
    "school_distribution": [0.5, 0.3, 0.2],
    "shopping_centers": 5,
    "disease": {"transmission_rate": 0.03, "recovery_rate": 0.01, "mortality_rate": 0.001}
}

if __name__ == "__main__":
    from disease import CovidModel
    from policies import LockdownPolicy, SocialDistancingPolicy

    simulation_controller = SimulationController(
        demographics=example_demographics,
        config=example_config,
        disease_model_class=CovidModel,
        policies=[LockdownPolicy, SocialDistancingPolicy],
        simulation_days=10
    )

    results = simulation_controller.run()
    print("Simulation Results:", results)
