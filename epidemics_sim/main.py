from simulation.microsimulation.synthethic_population import SyntheticPopulationGenerator
# from microsimulation.population_cluster import PopulationCluster
# from microsimulation.disease_propagation import DiseasePropagation
# from microsimulation.analysis import SimulationAnalyzer

def main():
    # Example demographics data
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
    num_homes = 300
    num_workplaces = 50
    num_schools = 20
    simulation_duration_days = 30  # Duración total de la simulación en días

    # Etapa 2: Generar la población sintética
    print("Generando población sintética...")
    generator = SyntheticPopulationGenerator(demographics=demographics_data)
    households, population = generator.generate_population()
    # Print example households
    for i, household in enumerate(households[:5]):
        print(f"Household {i+1}: {[agent.agent_id for agent in household]} with ages {[agent.age for agent in household]}")


    # # Etapa 3: Crear los clusters (hogar, trabajo, escuela)
    # print("Agrupando población en clusters...")
    # cluster_creator = PopulationCluster()
    # home_clusters = cluster_creator.create_home_clusters(population, num_homes)
    # work_clusters = cluster_creator.create_work_clusters(population, num_workplaces)
    # school_clusters = cluster_creator.create_school_clusters(population, num_schools)

    # # Etapa 4: Propagar la enfermedad
    # print("Simulando propagación de la enfermedad...")
    # disease_model = DiseasePropagation(simulation_duration=simulation_duration_days * 24 * 60)
    # disease_model.initialize_infection(population, initial_infected=5)  # Comenzamos con 5 infectados inicialmente
    # disease_model.simulate_spread(
    #     population,
    #     clusters={"home": home_clusters, "work": work_clusters, "school": school_clusters},
    #     duration_days=simulation_duration_days
    # )

    # # Etapa 5: Análisis de resultados
    # print("Analizando resultados...")
    # analyzer = SimulationAnalyzer(population)
    # analyzer.report_summary()
    # analyzer.plot_infection_curves()

if __name__ == "__main__":
    main()
