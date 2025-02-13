from epidemics_sim.simulation.clusters import CityClusterGenerator
from epidemics_sim.simulation.dailysim import DailySimulation
#from epidemics_sim.simulation.simulation_utils import SimulationAnalyzer
from epidemics_sim.policies.lockdown_policy import LockdownPolicy
from epidemics_sim.policies.social_distancing_policy import SocialDistancingPolicy
from epidemics_sim.policies.vaccination_policy import VaccinationPolicy
from epidemics_sim.policies.mask_policy import MaskUsagePolicy
from epidemics_sim.simulation.synthetic_population import SyntheticPopulationGenerator #TODO: Cambiar esto a intethic
from epidemics_sim.simulation.transport_interaction import TransportInteraction
from epidemics_sim.healthcare.healthcare_system import HealthcareSystem

class SimulationController:
    def __init__(self, demographics, disease, policies_config, simulation_days, initial_infected):
        """
        Initialize the simulation controller.

        :param demographics: Demographic data to generate agents.
        :param config: Configuration dictionary for the simulation.
        :param disease_model_class: Class of the disease model to use.
        :param policies: List of policy classes to apply.
        :param simulation_days: Number of days to simulate.
        """
        self.demographics = demographics
        self.disease_model = disease
        self.policies_config = policies_config 
        self.simulation_days = simulation_days
        self.initial_infected = initial_infected
        self.agents = self._generate_agents()
        self.cluster_generator = CityClusterGenerator(demographics)
        self.policies = self._configurate_policies(policies_config)
        self.heathcare_system = HealthcareSystem(5000, 10000, self.policies, self.demographics["municipios"])
        
    def _configurate_policies(self, policies_config):
        """
        Configura las políticas de la simulación según el diccionario 'policies'.
        
        :param policies: Diccionario con las políticas de la simulación.
        """
        policies = []
        # Configuración de la política de confinamiento (lockdown)
        if "lockdown" in policies_config:
            lockdown_config = policies_config["lockdown"]
            policies.append(LockdownPolicy(restricted_clusters=lockdown_config.get("restricted_clusters", [])))
        
        # Configuración de la política de uso de mascarillas (mask)
        if "mask" in policies_config:
            mask_config = policies_config["mask"]
            policies.append(MaskUsagePolicy(transmission_reduction_factor=mask_config.get("transmission_reduction_factor", 0)))
        
        # Configuración de la política de distanciamiento social (social_distancing)
        if "social_distancing" in policies_config:
            distancing_config = policies_config["social_distancing"]
            policies.append(SocialDistancingPolicy(reduction_factor=distancing_config.get("reduction_factor", 1)))
            
        
        # Configuración de la política de vacunación (vaccination)
        if "vaccination" in policies_config:
            vaccination_config = policies_config["vaccination"]
            policies.append(VaccinationPolicy(vaccination_rate=vaccination_config.get("vaccination_rate", 0), vaccine_efficacy=vaccination_config.get("vaccine_efficacy", 0)))
           
        
        print("Políticas configuradas")
        return policies
    
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
        
        # Initialize daily simulation
        daily_simulation = DailySimulation(
            agents=self.agents,
            cluster_generator=self.cluster_generator,
            disease_model=self.disease_model,
            policies=self.policies,
            healthcare_system=self.heathcare_system,
            initial_infected= self.initial_infected
        )

        # Run simulation for the specified number of days
        simulation_results = daily_simulation.simulate(self.simulation_days)


        return simulation_results

