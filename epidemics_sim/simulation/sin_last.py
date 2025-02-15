import pickle  # Para serialización y deserialización
from epidemics_sim.agents.human_agent import HumanAgent
import random

class SyntheticPopulationGenerator:
    def __init__(self, demographics):
        """
        Clase para generar una población sintética basada en los datos demográficos.
        
        :param demographics: Diccionario con datos demográficos.
        """
        self.demographics = demographics
        self.comorbidities_rates = demographics.get("Comorbilidades", {})  # Tasa de comorbilidades por mil
        self.population = {}
        self.agent_counter = 0  # Contador de agentes

    def generate_population(self):
        """
        Genera una población de agentes con atributos demográficos.
        """
        self._generate_agents()
        return self.population

    def save_population(self, agents, filepath):
        with open(filepath, 'wb') as file:
            pickle.dump(agents, file)
        print(f"Población guardada en {filepath}.")

    def load_population(self, filepath):
        with open(filepath, 'rb') as file:
            agents = pickle.load(file)
        print(f"Población cargada desde {filepath}.")
        return agents

    def _generate_agents(self):
        for municipio, data in self.demographics["municipios"].items():
            # Obtener datos de población en edad laboral y no laboral
            poblacion_laboral = data.get("Poblacion_Edad_Laboral", {})
            if not poblacion_laboral:
                continue  # Si no hay datos, ignorar este municipio

            # Obtener el número de hombres y mujeres en edad laboral y no laboral
            hombres_laboral = poblacion_laboral["Edad_Laboral"].get("Hombres", 0)
            mujeres_laboral = poblacion_laboral["Edad_Laboral"].get("Mujeres", 0)
            hombres_no_laboral = poblacion_laboral["Fuera_Edad_Laboral"].get("Hombres", 0)
            mujeres_no_laboral = poblacion_laboral["Fuera_Edad_Laboral"].get("Mujeres", 0)

            # Generar agentes para hombres y mujeres
            self._create_agents(hombres_laboral, "male", municipio, data, is_laboral=True)
            self._create_agents(mujeres_laboral, "female", municipio, data, is_laboral=True)
            self._create_agents(hombres_no_laboral, "male", municipio, data, is_laboral=False)
            self._create_agents(mujeres_no_laboral, "female", municipio, data, is_laboral=False)

    def _create_agents(self, num_agents, gender, municipio, data, is_laboral):
        for _ in range(num_agents):
            age = self._generate_age(data["population"]["Habitantes_por_edad"], is_laboral, gender)
            occupation = self._generate_occupation(is_laboral,age, gender)
            comorbidities = self._generate_comorbidities()

            # Generar un ID único para cada agente
            agent_id = self.agent_counter
            self.agent_counter += 1

            # Asegurarse de que la edad no sea None
            if age is None:
                raise ValueError(f"Edad no generada correctamente para el agente {agent_id}")

            agent = HumanAgent(
                agent_id, age, gender, occupation, None, municipio, None, comorbidities
            )
            self.population[agent_id] = agent

    def _generate_age(self, age_distribution, is_laboral, gender):
        """
        Genera una edad basada en la distribución por rangos de edad y el género.
        Si está en edad laboral, genera una edad dentro del rango laboral según el género.
        Si no está en edad laboral, genera una edad fuera de ese rango.
        """
        if is_laboral:
            # Si está en edad laboral, generar una edad dentro del rango laboral según el género
            if gender == "male":
                return random.randint(17, 64)  # Hombres: 17 a 64 años
            else:
                return random.randint(17, 59)  # Mujeres: 17 a 59 años
        else:
            # Si está fuera de la edad laboral, generar una edad basada en la distribución
            ranges = list(age_distribution.keys())
            probabilities = [float(age_distribution[r]) for r in ranges]
            chosen_range = random.choices(ranges, probabilities)[0]

            if chosen_range == "0-15":
                return random.randint(0, 15)
            elif chosen_range == "60 y +":
                # Para hombres, el rango es 65+; para mujeres, es 60+
                if gender == "male":
                    return random.randint(65, 100)
                else:
                    return random.randint(60, 100)
            else :
                a = 9    

    def _generate_occupation(self, is_laboral, age, gender):
        """
        Asigna una ocupación basada en si la persona está en edad laboral, su edad y su género.
        """
        if is_laboral:
            # Si está en edad laboral
            if 17 <= age <= 22:
                # Entre 17 y 22 años, 50% de probabilidad de ser estudiante o trabajador
                return "student" if random.random() < 0.5 else "worker"
            else:
                # Mayor de 22 años, trabajador
                return "worker"
        else:
            # Si no está en edad laboral
            if age < 17:
                # Menor de 17 años, estudiante
                return "student"
            else:
                # Jubilado: hombres mayores de 64, mujeres mayores de 59
                if gender == "male" and age >= 65:
                    return "retired"
                elif gender == "female" and age >= 60:
                    return "retired"
                else:
                    # En caso de que no se cumplan las condiciones anteriores
                    return "retired"

    def _generate_comorbidities(self):
        """
        Genera comorbilidades basadas en las tasas proporcionadas.
        """
        comorbidities = []
        for disease, rate_per_thousand in self.comorbidities_rates.items():
            probability = float(rate_per_thousand) / 1000  # Convertimos tasa por mil a probabilidad 0-1
            if random.random() < probability:
                comorbidities.append(disease)
        return comorbidities