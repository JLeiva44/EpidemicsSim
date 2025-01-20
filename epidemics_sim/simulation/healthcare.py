from collections import defaultdict
import random
from abc import ABC, abstractmethod

class HealthcareSystem:
    def __init__(self, municipalities, recovery_rates, mortality_rates):
        """
        Initialize the healthcare system.

        :param municipalities: Dictionary containing municipality data with healthcare structures.
        :param recovery_rates: Recovery rates for each level of care.
        :param mortality_rates: Mortality rates for each level of care.
        """
        self.municipalities = municipalities
        self.consultorios = self._initialize_units("consultorios", Consultorio)
        self.policlinicos = self._initialize_units("policlinicos", Policlinico)
        self.hospitals = self._initialize_units("hospitales", Hospital)
        self.recovery_rates = recovery_rates
        self.mortality_rates = mortality_rates

    def _initialize_units(self, key, unit_class):
        """
        Initialize healthcare units for each municipality.

        :param key: Key to access the number of units per municipality.
        :param unit_class: Class of the healthcare unit to instantiate.
        :return: Dictionary of initialized units.
        """
        key1 = "infraestructura_salud"
        units = {}
        for municipio, data in self.municipalities.items():
            units[municipio] = [unit_class(f"{unit_class.__name__}_{i}", municipio) for i in range(data["infraestructura_salud"][key])]
        return units

    def notify_infection(self, agent):
        """
        Notify the healthcare system of an infected agent.

        :param agent: The agent to evaluate and assign to care.
        """
        municipio = agent.municipio
        assigned = False

        # Attempt to assign to a consultorio
        for consultorio in self.consultorios[municipio]:
            if consultorio.handle_agent(agent, self.recovery_rates["consultorio"], self.mortality_rates["consultorio"]):
                assigned = True
                break

        # If not resolved, escalate to policlinico
        if not assigned:
            for policlinico in self.policlinicos[municipio]:
                if policlinico.handle_agent(agent, self.recovery_rates["policlinico"], self.mortality_rates["policlinico"]):
                    assigned = True
                    break

        # If not resolved, escalate to hospital
        if not assigned:
            for hospital in self.hospitals[municipio]:
                hospital.handle_agent(agent, self.recovery_rates["hospital"], self.mortality_rates["hospital"])

    def daily_operations(self):
        """
        Perform daily operations for all healthcare levels.
        """
        for units in [self.consultorios, self.policlinicos, self.hospitals]:
            for unit_list in units.values():
                for unit in unit_list:
                    unit.daily_process()

class HealthcareUnit(ABC):
    def __init__(self, name, municipio):
        self.name = name
        self.municipio = municipio
        self.patients = []

    @abstractmethod
    def handle_agent(self, agent, recovery_rate, mortality_rate):
        pass

    def daily_process(self):
        """
        Process daily operations, treating patients.
        """
        for patient in self.patients:
            if random.random() < self.recovery_rate:  # Use recovery rate for the unit
                patient.infection_status["state"] = "recovered"
                patient.immune = True
            elif random.random() < self.mortality_rate:  # Use mortality rate for the unit
                patient.infection_status["state"] = "deceased"
        self.patients = [p for p in self.patients if p.infection_status["state"] == "infected"]

class Consultorio(HealthcareUnit):
    def handle_agent(self, agent, recovery_rate, mortality_rate):
        """
        Attempt to treat the agent at the consultorio level.

        :param agent: The agent to treat.
        :param recovery_rate: Recovery rate for consultorios.
        :param mortality_rate: Mortality rate for consultorios.
        :return: True if the agent is handled here, False otherwise.
        """
        self.recovery_rate = recovery_rate
        self.mortality_rate = mortality_rate
        if agent.infection_status["severity"] == "mild":
            self.patients.append(agent)
            return True
        return False

class Policlinico(HealthcareUnit):
    def handle_agent(self, agent, recovery_rate, mortality_rate):
        """
        Attempt to treat the agent at the policlinico level.

        :param agent: The agent to treat.
        :param recovery_rate: Recovery rate for policlinicos.
        :param mortality_rate: Mortality rate for policlinicos.
        :return: True if the agent is handled here, False otherwise.
        """
        self.recovery_rate = recovery_rate
        self.mortality_rate = mortality_rate
        if agent.infection_status["severity"] in ["moderate", "severe"]:
            self.patients.append(agent)
            return True
        return False

class Hospital(HealthcareUnit):
    def handle_agent(self, agent, recovery_rate, mortality_rate):
        """
        Attempt to treat the agent at the hospital level.

        :param agent: The agent to treat.
        :param recovery_rate: Recovery rate for hospitals.
        :param mortality_rate: Mortality rate for hospitals.
        :return: True since all unresolved cases are handled here.
        """
        self.recovery_rate = recovery_rate
        self.mortality_rate = mortality_rate
        self.patients.append(agent)
        return True

    def daily_process(self):
        """
        Process daily operations, treating patients at the hospital level.
        """
        for patient in self.patients:
            if random.random() < self.recovery_rate:
                patient.infection_status["state"] = "recovered"
                patient.immune = True
            elif random.random() < self.mortality_rate:
                patient.infection_status["state"] = "deceased"
        self.patients = [p for p in self.patients if p.infection_status["state"] == "infected"]
