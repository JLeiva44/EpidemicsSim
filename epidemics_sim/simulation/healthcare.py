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
        :param state_manager: Instance of StateManager to handle state transitions.
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
        :param state_manager: Instance of StateManager to handle state transitions.
        :return: Dictionary of initialized units.
        """
        units = {}
        for municipio, data in self.municipalities.items():
            num_units = data["infraestructura_salud"].get(key, 0)
            units[municipio] = [
                unit_class(f"{unit_class.__name__}_{i}", municipio)
                for i in range(num_units)
            ]
        return units

    def notify_infection(self, agent, disease_model):
        """
        Notify the healthcare system of an infected agent.

        :param agent: The agent to evaluate and assign to care.
        :param disease_model: The disease model for calculating dynamic rates.
        """
        municipio = agent.municipio
        assigned = False

        # Attempt to assign to a consultorio
        for consultorio in self.consultorios[municipio]:
            if consultorio.handle_agent(agent, self.recovery_rates["consultorio"], self.mortality_rates["consultorio"], disease_model):
                assigned = True
                break

        # If not resolved, escalate to policlinico
        if not assigned:
            for policlinico in self.policlinicos[municipio]:
                if policlinico.handle_agent(agent, self.recovery_rates["policlinico"], self.mortality_rates["policlinico"], disease_model):
                    assigned = True
                    break

        # If not resolved, escalate to hospital
        if not assigned:
            for hospital in self.hospitals[municipio]:
                hospital.handle_agent(agent, self.recovery_rates["hospital"], self.mortality_rates["hospital"], disease_model)

    def daily_operations(self):
        """
        Perform daily operations for all healthcare levels.
        """
        for units in [self.consultorios, self.policlinicos, self.hospitals]:
            for unit_list in units.values():
                for unit in unit_list:
                    unit.daily_process()

class HealthcareUnit(ABC):
    def __init__(self, name, municipio, capacity=float('inf')):
        self.name = name
        self.municipio = municipio
        self.capacity = capacity
        self.patients = []

    @abstractmethod
    def handle_agent(self, agent, recovery_rate, mortality_rate, disease_model):
        pass

    # def daily_process(self):
    #     """
    #     Process daily operations, treating patients by delegating to the state manager.
    #     """
    #     for patient in self.patients:
    #         self.state_manager.evaluate_state(
    #             patient,
    #             recovery_rate=self.recovery_rate,
    #             mortality_rate=self.mortality_rate
    #         )
    #     # Remove patients who are no longer infected
    #     self.patients = [p for p in self.patients if p.state == State.INFECTED]

class Consultorio(HealthcareUnit):
    def handle_agent(self, agent, recovery_rate, mortality_rate, disease_model):
        """
        Attempt to treat the agent at the consultorio level.

        :param agent: The agent to treat.
        :param recovery_rate: Recovery rate for consultorios.
        :param mortality_rate: Mortality rate for consultorios.
        :param disease_model: Disease model for dynamic adjustments.
        :return: True if the agent is handled here, False otherwise.
        """
        self.recovery_rate, self.mortality_rate = disease_model.adjust_rates("consultorio", recovery_rate, mortality_rate)
        if agent.infection_status["severity"] == "mild" and len(self.patients) < self.capacity:
            self.patients.append(agent)
            return True
        return False

class Policlinico(HealthcareUnit):
    def handle_agent(self, agent, recovery_rate, mortality_rate, disease_model):
        """
        Attempt to treat the agent at the policlinico level.

        :param agent: The agent to treat.
        :param recovery_rate: Recovery rate for policlinicos.
        :param mortality_rate: Mortality rate for policlinicos.
        :param disease_model: Disease model for dynamic adjustments.
        :return: True if the agent is handled here, False otherwise.
        """
        self.recovery_rate, self.mortality_rate = disease_model.adjust_rates("policlinico", recovery_rate, mortality_rate)
        if agent.infection_status["severity"] in ["moderate", "severe"] and len(self.patients) < self.capacity:
            self.patients.append(agent)
            return True
        return False

class Hospital(HealthcareUnit):
    def handle_agent(self, agent, recovery_rate, mortality_rate, disease_model):
        """
        Attempt to treat the agent at the hospital level.

        :param agent: The agent to treat.
        :param recovery_rate: Recovery rate for hospitals.
        :param mortality_rate: Mortality rate for hospitals.
        :param disease_model: Disease model for dynamic adjustments.
        :return: True since all unresolved cases are handled here.
        """
        self.recovery_rate, self.mortality_rate = disease_model.adjust_rates("hospital", recovery_rate, mortality_rate)
        if len(self.patients) < self.capacity:
            self.patients.append(agent)
        return True
