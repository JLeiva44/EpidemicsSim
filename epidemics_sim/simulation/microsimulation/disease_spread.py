class DiseasePropagation:
    def __init__(self, simulation_duration, time_step=5):
        """
        Initialize the disease propagation simulation.

        :param simulation_duration: Total simulation duration in minutes.
        :param time_step: Time step for each iteration (in minutes).
        """
        self.simulation_duration = simulation_duration
        self.time_step = time_step

    def initialize_infection(self, population, initial_infected=1):
        """
        Initialize the simulation by infecting a small number of individuals.

        :param population: List of agents in the population.
        :param initial_infected: Number of individuals to infect initially.
        """
        import random
        infected_agents = random.sample(population, initial_infected)
        for agent in infected_agents:
            agent["status"] = "infected"
            agent["time_since_infection"] = 0  # Time since infection in minutes
            agent["severity"] = None  # To be determined later

    def simulate_spread(self, population, clusters, duration_days):
        """
        Simulate the spread of the disease.

        :param population: List of agents in the population.
        :param clusters: Dictionary of clusters (e.g., home, work, school).
        :param duration_days: Number of days to simulate.
        """
        total_minutes = duration_days * 24 * 60
        current_time = 0

        while current_time < total_minutes:
            for agent in population:
                if agent["status"] == "infected":
                    self._progress_infection(agent)
                self._simulate_social_interaction(agent, clusters)
            
            # Advance time
            current_time += self.time_step

    def _progress_infection(self, agent):
        """
        Progress the infection for an individual agent.

        :param agent: The agent being evaluated.
        """
        if "time_since_infection" in agent:
            agent["time_since_infection"] += self.time_step

            # Assign severity after diagnosis
            if agent["severity"] is None and agent["time_since_infection"] > 60:  # 1 hour
                agent["severity"] = self._determine_severity()

    def _simulate_social_interaction(self, agent, clusters):
        """
        Simulate the social interactions for an agent.

        :param agent: The agent being evaluated.
        :param clusters: Dictionary of clusters.
        """
        import random

        # Example: Interact with members of the same home cluster
        home_cluster = clusters.get("home", {}).get(agent["id"], [])
        for contact in home_cluster:
            if contact["status"] == "infected" and agent["status"] == "susceptible":
                self._attempt_infection(agent)

    def _attempt_infection(self, agent):
        """
        Attempt to infect a susceptible agent.

        :param agent: The susceptible agent.
        """
        import random
        infection_probability = 0.1  # Example value
        if random.random() < infection_probability:
            agent["status"] = "infected"
            agent["time_since_infection"] = 0
            agent["severity"] = None

    def _determine_severity(self):
        """
        Determine the severity of the disease for an infected individual.

        :return: A string representing the severity level.
        """
        import random
        severity_levels = ["mild", "moderate", "severe", "critical"]
        probabilities = [0.6, 0.25, 0.1, 0.05]  # Example probabilities
        return random.choices(severity_levels, probabilities)[0]
