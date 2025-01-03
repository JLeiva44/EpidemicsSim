if __name__ == "__main__":
    from epidemics_sim.simulation.microsimulation.population_clusters import HomeCluster, WorkCluster, SchoolCluster, ShoppingCluster
    from epidemics_sim.simulation.microsimulation.population_clusters import TransportInteraction
    from epidemics_sim.agents.human_agent import HumanAgent
    from epidemics_sim.simulation.microsimulation.dailysim import DailySimulation
    from epidemics_sim.policies.lockdown_policy import LockdownPolicy
    from epidemics_sim.policies.social_distancing_policy import SocialDistancingPolicy
    from epidemics_sim.policies.vaccination_policy import VaccinationPolicy
    from epidemics_sim.diseases.covid_model import CovidModel
    from epidemics_sim.simulation.microsimulation.synthethic_population import SyntheticPopulationGenerator 
    from logger import logger
    #region Example configuration 
    example_config = {
        "home": {"duration_mean": 480, "duration_std": 120},
        "work": {"duration_mean": 480, "duration_std": 120, "min_links": 2},
        "school": {"duration_mean": 300, "duration_std": 60},
        "shopping": {"duration_mean": 37, "duration_std": 10, "max_agents": 50},
        "transport": {"interval": 5, "duration_mean": 15, "duration_std": 5},
    }
    demographics_data = {
        "num_agents": 100,
        "age_distribution": {
            "0-17": 0.25,
            "18-64": 0.6,
            "65+": 0.15
        },
        "gender_distribution": {
            "male": 0.5,
            "female": 0.5
        },
        "household_size_distribution": [1, 2, 3, 4, 5, 6, 7],
        "household_size_probabilities": [0.3, 0.25, 0.2, 0.15, 0.05, 0.03, 0.02],
        "num_households": 50,
        "comorbidity_distribution": {
            "diabetes": {"base": 0.1, "age": {"40+": 0.2}},
            "hypertension": {"base": 0.15, "age": {"40+": 0.3}},
            "obesity": {"base": 0.2},
            "smoking": {"base": 0.25, "gender": {"male": 0.3, "female": 0.2}},
            "copd": {"base": 0.05, "age": {"50+": 0.1}},
            "chronic_heart_disease": {"base": 0.07, "age": {"50+": 0.15}},
            "chronic_kidney_disease": {"base": 0.03}
        }
    }
    #endregion


    #region Inicialización de agentes
    num_agents = 100
    population_generator = SyntheticPopulationGenerator(demographics=demographics_data)
    agents = population_generator.generate_population()
    # for agent in agents:
    #     logger.info(agent)

    #region Inicialización de clusters
    home_clusters = [HomeCluster(agents[i:i + 5], example_config["home"]) for i in range(0, 20, 5)]
    work_clusters = [WorkCluster(agents[i:i + 10], example_config["work"]) for i in range(20, 50, 10)]
    school_clusters = [SchoolCluster(agents[i:i + 10], example_config["school"]) for i in range(50, 80, 10)]
    shopping_clusters = [ShoppingCluster(agents[i:i + 10], example_config["shopping"]) for i in range(80, 100, 10)]

    clusters = {
        "home": home_clusters,
        "work": work_clusters,
        "school": school_clusters,
        "shopping": shopping_clusters,
    }

    # Transporte
    transport_interaction = TransportInteraction(agents, example_config["transport"])

    #endregion

    # Modelo de enfermedad
    covid_model = CovidModel(transmission_rate=0.05, recovery_rate=0.01)

    # Políticas activas
    policies = [
        LockdownPolicy(restricted_clusters=["work", "school"]),
        SocialDistancingPolicy(reduction_factor=0.5),
        VaccinationPolicy(vaccination_rate=0.1),
    ]

    # Simulación diaria
    simulation = DailySimulation(agents, clusters, transport_interaction, example_config, covid_model, policies)

    # Ejecutar la simulación por 10 días
    results = simulation.simulate(days=10)

    # Mostrar resultados
    for day, result in enumerate(results, start=1):
        print(f"Day {day}:")
        print(result)
