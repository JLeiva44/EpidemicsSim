from epidemics_sim.simulation.clusters import CityClusterGenerator
from epidemics_sim.simulation.dailysim import DailySimulation
#from epidemics_sim.simulation.simulation_utils import SimulationAnalyzer
from epidemics_sim.policies.lockdown_policy import LockdownPolicy
from epidemics_sim.policies.social_distancing_policy import SocialDistancingPolicy
from epidemics_sim.policies.vaccination_policy import VaccinationPolicy
from epidemics_sim.simulation.synthetic_population import SyntheticPopulationGenerator #TODO: Cambiar esto a intethic
from epidemics_sim.simulation.transport_interaction import TransportInteraction
from epidemics_sim.healthcare.healthcare_system import HealthcareSystem

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
        self.policies = self._configurate_policies(policies) #[policy() for policy in policies]
        self.simulation_days = simulation_days
        self.agents = self._generate_agents()
        self.cluster_generator = CityClusterGenerator(demographics)
        #self.analyzer = SimulationAnalyzer()

    def _configurate_policies(self, policies):
        configured_policies = []
        for policy in policies:
            if policy.__name__ == "LockdownPolicy":
                configured_policies.append(LockdownPolicy())  # Restricted_clusters arg
            elif policy.__name__ == "SocialDistancingPolicy":
                configured_policies.append(SocialDistancingPolicy(0.5))  # Social_distance_factor arg
            elif policy.__name__ == "VaccinationPolicy":
                configured_policies.append(VaccinationPolicy(0.5, 0.8))  # Vaccination_rate arg
        return configured_policies
    
    def _generate_agents(self):
        """
        Generate a synthetic population based on demographic data.

        :return: List of generated agents.
        """

        generator = SyntheticPopulationGenerator(
            demographics=self.demographics
        )
        agents = generator.generate_population()
        print("se genero la poblacion")
        generator.save_population(agents,'population.pkl')
        print("Se salvo")
        agents = generator.load_population('population.pkl')
        print("Se cargo")
        return agents

    def run(self):
        """
        Run the simulation.

        :return: Results of the simulation.
        """
        # Generate transport interactions
        #transport_interaction = TransportInteraction(self.agents, self.config["transport"])

        # Initialize the disease model
        disease_model = self.disease_model_class(**self.config["disease"])

        # Initialize the HealthCare System TODO: Meter las capacidades en el json
        healthcare_system = HealthcareSystem(5000, 10000,self.policies, self.demographics["municipios"]) # Aqui tengo que anadir las politicas

        # Initialize daily simulation
        daily_simulation = DailySimulation(
            agents=self.agents,
            cluster_generator=self.cluster_generator,
            transport=None,
            config=self.config,
            disease_model=disease_model,
            policies=self.policies,
            healthcare_system=healthcare_system,
        )

        # Run simulation for the specified number of days
        simulation_results = daily_simulation.simulate(self.simulation_days)

        # # Record daily statistics
        # for _ in range(self.simulation_days):
        #     self.analyzer.record_daily_stats(self.agents)

        # Generate results
        # report = self.analyzer.generate_report()
        # self.analyzer.plot_statistics()

        return simulation_results

