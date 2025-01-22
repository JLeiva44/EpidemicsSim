import networkx as nx
import numpy as np

class GraphValidator:
    def __init__(self, graph):
        """
        Initialize the GraphValidator.

        :param graph: NetworkX graph to validate and analyze.
        """
        self.graph = graph

    def is_scale_free(self):
        """
        Check if the graph follows a scale-free distribution by analyzing its degree distribution.

        :return: True if the graph approximately follows a power-law distribution, False otherwise.
        """
        degrees = [degree for _, degree in self.graph.degree()]
        if len(degrees) < 2:
            return False

        # Fit the degree distribution to a power-law
        try:
            fit = np.polyfit(np.log(range(1, len(degrees) + 1)), np.log(sorted(degrees, reverse=True)), 1)
            slope = fit[0]
            return -3 <= slope <= -2  # Typical range for scale-free networks
        except Exception:
            return False

    def calculate_metrics(self):
        """
        Calculate key metrics of the graph.

        :return: Dictionary of graph metrics.
        """
        metrics = {
            "num_nodes": self.graph.number_of_nodes(),
            "num_edges": self.graph.number_of_edges(),
            "average_degree": np.mean([degree for _, degree in self.graph.degree()]),
            "clustering_coefficient": nx.average_clustering(self.graph),
            "average_shortest_path": nx.average_shortest_path_length(self.graph) if nx.is_connected(self.graph) else None,
            "degree_assortativity": nx.degree_assortativity_coefficient(self.graph),
        }
        return metrics

    def identify_hubs(self, threshold=0.05):
        """
        Identify hub nodes in the graph.

        :param threshold: Fraction of top nodes to consider as hubs (default: 5%).
        :return: List of hub nodes.
        """
        num_hubs = max(1, int(threshold * self.graph.number_of_nodes()))
        sorted_nodes = sorted(self.graph.degree(), key=lambda x: x[1], reverse=True)
        hubs = [node for node, _ in sorted_nodes[:num_hubs]]
        return hubs

    def validate(self):
        """
        Perform a full validation of the graph, checking its scale-free properties and calculating metrics.

        :return: Dictionary containing validation results.
        """
        return {
            "is_scale_free": self.is_scale_free(),
            "metrics": self.calculate_metrics(),
            "hubs": self.identify_hubs()
        }

# Example usage
if __name__ == "__main__":
    # Create an example scale-free graph
    example_graph = nx.barabasi_albert_graph(100, 3)

    validator = GraphValidator(example_graph)
    results = validator.validate()

    print("Validation Results:")
    print(f"Scale-Free: {results['is_scale_free']}")
    print("Metrics:")
    for metric, value in results['metrics'].items():
        print(f"  {metric}: {value}")
    print("Hubs:", results["hubs"])
