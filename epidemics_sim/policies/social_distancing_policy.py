from epidemics_sim.policies.base_policy import Policy

class SocialDistancingPolicy(Policy):
    def __init__(self, reduction_factor=0.5):
        """
        Inicializa la política de distanciamiento social.

        :param reduction_factor: Factor por el cual se reducirá la probabilidad de interacción en los clusters.
        """
        self.reduction_factor = reduction_factor
        self.affected_clusters = {}  # Para almacenar el valor original de interacción de cada cluster

    def enforce(self, agents, clusters):
        """
        Aplica la política de distanciamiento social reduciendo la probabilidad de interacción en los clusters.

        :param agents: Diccionario de agentes (no se usa en esta política).
        :param clusters: Diccionario de clusters en la simulación.
        """
        self.affected_clusters = {}  # Reset de valores originales antes de aplicar

        for cluster_type, cluster in clusters.items():
            original_prob = cluster.interaction_probability
            new_prob = original_prob * self.reduction_factor
            self.affected_clusters[cluster] = original_prob  # Guardar el valor original
            cluster.interaction_probability = max(0.05, new_prob)  # Límite inferior para evitar 0 absoluto

        print(f"📉 Política de Distanciamiento Social aplicada. Reducción de interacción en un {self.reduction_factor * 100:.0f}%")

    def delete(self, agents, clusters):
        """
        Revierte la política restaurando la probabilidad de interacción original en los clusters.

        :param agents: Diccionario de agentes (no se usa en esta política).
        :param clusters: Diccionario de clusters en la simulación.
        """
        for cluster, original_prob in self.affected_clusters.items():
            cluster.interaction_probability = original_prob  # Restaurar valor original

        self.affected_clusters = {}  # Limpiar estado
        print("🔄 Se ha eliminado la Política de Distanciamiento Social. Se restauraron las interacciones.")

    def __str__(self):
        return "Social Distancing Policy"
