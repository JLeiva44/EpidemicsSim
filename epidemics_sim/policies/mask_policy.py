from epidemics_sim.policies.base_policy import Policy

class MaskUsagePolicy(Policy):
    def __init__(self, transmission_reduction_factor=0.7):
        """
        :param transmission_reduction_factor: Factor de reducción en la probabilidad de transmisión (0 a 1).
        """
        self.transmission_reduction_factor = transmission_reduction_factor

    def enforce(self, agents, clusters):
        """
        Reduce la probabilidad de transmisión de la enfermedad mediante el uso de mascarillas.
        """
        for agent in agents:
            agent.mask["usage"] = True
            agent.mask["reduction_factor"] = 0.7

    def delete(self, agents, clusters):
        """
        Restaura la probabilidad de transmisión a su valor original eliminando la política de mascarillas.
        """
        for agent in agents:
            agent.mask["usage"] = False
            agent.mask["reduction_factor"] = 1.0
    
    def __str__(self):
        return "Mask Usage Policy"
