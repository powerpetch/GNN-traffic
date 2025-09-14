"""
Graph construction module for creating road network graphs for GNN models.
Builds spatial-temporal graphs from road network and traffic data.
"""

import pandas as pd
import numpy as np
import networkx as nx
from typing import Dict, List, Tuple, Optional, Union
import logging
from scipy.spatial.distance import cdist

class GraphBuilder:
    """Builds graphs for GNN traffic prediction models."""
    
    def __init__(self, distance_threshold: float = 1000.0):
        """
        Initialize graph builder.
        
        Args:
            distance_threshold: Maximum distance (meters) for edge connections
        """
        self.distance_threshold = distance_threshold
        self.logger = logging.getLogger(__name__)
        
    def build_spatial_graph(self, road_segments: pd.DataFrame) -> nx.Graph:
        """
        Build spatial graph from road segments.
        
        Args:
            road_segments: DataFrame with road segment information
            
        Returns:
            NetworkX graph with spatial connections
        """
        G = nx.Graph()
        
        # Add nodes (road segments)
        for idx, segment in road_segments.iterrows():
            node_id = segment.get('osm_id', idx)
            G.add_node(node_id, **segment.to_dict())
        
        # Add edges based on spatial proximity
        nodes = list(G.nodes(data=True))
        
        for i, (node_i, data_i) in enumerate(nodes):
            for j, (node_j, data_j) in enumerate(nodes[i+1:], i+1):
                distance = self._calculate_distance(data_i, data_j)
                
                if distance <= self.distance_threshold:
                    G.add_edge(node_i, node_j, distance=distance, weight=1.0/distance)
        
        self.logger.info(f"Built spatial graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        return G
    
    def _calculate_distance(self, segment1: Dict, segment2: Dict) -> float:
        """
        Calculate distance between two road segments.
        
        Args:
            segment1: First segment data
            segment2: Second segment data
            
        Returns:
            Distance in meters
        """
        # Use centroid coordinates if available
        lat1 = segment1.get('avg_lat', segment1.get('lat', 0))
        lon1 = segment1.get('avg_lon', segment1.get('lon', 0))
        lat2 = segment2.get('avg_lat', segment2.get('lat', 0))
        lon2 = segment2.get('avg_lon', segment2.get('lon', 0))
        
        # Haversine distance approximation
        R = 6371000  # Earth radius in meters
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        
        a = (np.sin(dlat/2) * np.sin(dlat/2) + 
             np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * 
             np.sin(dlon/2) * np.sin(dlon/2))
        
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        distance = R * c
        
        return distance
    
    def create_adjacency_matrix(self, graph: nx.Graph, 
                               node_order: Optional[List] = None) -> np.ndarray:
        """
        Create adjacency matrix from graph.
        
        Args:
            graph: NetworkX graph
            node_order: Optional list specifying node order
            
        Returns:
            Adjacency matrix as numpy array
        """
        if node_order is None:
            node_order = list(graph.nodes())
        
        n_nodes = len(node_order)
        adj_matrix = np.zeros((n_nodes, n_nodes))
        
        node_to_idx = {node: idx for idx, node in enumerate(node_order)}
        
        for edge in graph.edges(data=True):
            i = node_to_idx[edge[0]]
            j = node_to_idx[edge[1]]
            weight = edge[2].get('weight', 1.0)
            
            adj_matrix[i, j] = weight
            adj_matrix[j, i] = weight  # Undirected graph
            
        return adj_matrix
    
    def add_self_loops(self, adj_matrix: np.ndarray) -> np.ndarray:
        """Add self-loops to adjacency matrix."""
        return adj_matrix + np.eye(adj_matrix.shape[0])
    
    def normalize_adjacency(self, adj_matrix: np.ndarray, 
                          method: str = 'symmetric') -> np.ndarray:
        """
        Normalize adjacency matrix for GNN.
        
        Args:
            adj_matrix: Adjacency matrix
            method: Normalization method ('symmetric', 'row', 'column')
            
        Returns:
            Normalized adjacency matrix
        """
        if method == 'symmetric':
            # D^(-1/2) * A * D^(-1/2)
            degree = np.sum(adj_matrix, axis=1)
            degree_inv_sqrt = np.power(degree, -0.5)
            degree_inv_sqrt[np.isinf(degree_inv_sqrt)] = 0.0
            
            degree_matrix_inv_sqrt = np.diag(degree_inv_sqrt)
            normalized = degree_matrix_inv_sqrt @ adj_matrix @ degree_matrix_inv_sqrt
            
        elif method == 'row':
            # D^(-1) * A
            degree = np.sum(adj_matrix, axis=1)
            degree_inv = np.power(degree, -1.0)
            degree_inv[np.isinf(degree_inv)] = 0.0
            
            degree_matrix_inv = np.diag(degree_inv)
            normalized = degree_matrix_inv @ adj_matrix
            
        elif method == 'column':
            # A * D^(-1)
            degree = np.sum(adj_matrix, axis=0)
            degree_inv = np.power(degree, -1.0)
            degree_inv[np.isinf(degree_inv)] = 0.0
            
            degree_matrix_inv = np.diag(degree_inv)
            normalized = adj_matrix @ degree_matrix_inv
            
        else:
            raise ValueError(f"Unknown normalization method: {method}")
            
        return normalized
    
    def create_temporal_edges(self, time_series_df: pd.DataFrame,
                            temporal_window: int = 3) -> List[Tuple]:
        """
        Create temporal edges for spatial-temporal graph.
        
        Args:
            time_series_df: Time series data
            temporal_window: Number of time steps for temporal connections
            
        Returns:
            List of temporal edges
        """
        temporal_edges = []
        
        # Sort by road_id and time
        df_sorted = time_series_df.sort_values(['road_id', 'time_bin'])
        
        for road_id, group in df_sorted.groupby('road_id'):
            time_indices = group.index.tolist()
            
            # Create temporal connections within window
            for i in range(len(time_indices)):
                for j in range(1, min(temporal_window + 1, len(time_indices) - i)):
                    current_idx = time_indices[i]
                    future_idx = time_indices[i + j]
                    
                    # Edge weight decreases with temporal distance
                    weight = 1.0 / j
                    temporal_edges.append((current_idx, future_idx, weight))
        
        return temporal_edges
    
    def build_spatial_temporal_graph(self, road_segments: pd.DataFrame,
                                   time_series_df: pd.DataFrame) -> Tuple[nx.Graph, Dict]:
        """
        Build combined spatial-temporal graph.
        
        Args:
            road_segments: Road segment information
            time_series_df: Time series traffic data
            
        Returns:
            Tuple of (graph, metadata)
        """
        # Build spatial graph
        spatial_graph = self.build_spatial_graph(road_segments)
        
        # Create spatial-temporal graph
        st_graph = nx.Graph()
        
        # Add spatial-temporal nodes (road_id, time_bin)
        for idx, row in time_series_df.iterrows():
            node_id = (row['road_id'], row['time_bin'])
            st_graph.add_node(node_id, **row.to_dict())
        
        # Add spatial edges (same time, connected roads)
        for time_bin in time_series_df['time_bin'].unique():
            time_data = time_series_df[time_series_df['time_bin'] == time_bin]
            
            for edge in spatial_graph.edges(data=True):
                road1, road2 = edge[0], edge[1]
                
                if (road1 in time_data['road_id'].values and 
                    road2 in time_data['road_id'].values):
                    
                    node1 = (road1, time_bin)
                    node2 = (road2, time_bin)
                    
                    if st_graph.has_node(node1) and st_graph.has_node(node2):
                        st_graph.add_edge(node1, node2, 
                                        edge_type='spatial',
                                        weight=edge[2]['weight'])
        
        # Add temporal edges
        temporal_edges = self.create_temporal_edges(time_series_df)
        
        for edge in temporal_edges:
            idx1, idx2, weight = edge
            row1 = time_series_df.iloc[idx1]
            row2 = time_series_df.iloc[idx2]
            
            node1 = (row1['road_id'], row1['time_bin'])
            node2 = (row2['road_id'], row2['time_bin'])
            
            if st_graph.has_node(node1) and st_graph.has_node(node2):
                st_graph.add_edge(node1, node2, 
                                edge_type='temporal',
                                weight=weight)
        
        metadata = {
            'n_nodes': st_graph.number_of_nodes(),
            'n_edges': st_graph.number_of_edges(),
            'spatial_edges': len([e for e in st_graph.edges(data=True) 
                                if e[2]['edge_type'] == 'spatial']),
            'temporal_edges': len([e for e in st_graph.edges(data=True) 
                                 if e[2]['edge_type'] == 'temporal'])
        }
        
        self.logger.info(f"Built spatial-temporal graph: {metadata}")
        return st_graph, metadata
    
    def extract_subgraphs(self, graph: nx.Graph, 
                         node_sets: List[List]) -> List[nx.Graph]:
        """
        Extract subgraphs for batch processing.
        
        Args:
            graph: Full graph
            node_sets: List of node sets for each subgraph
            
        Returns:
            List of subgraphs
        """
        subgraphs = []
        
        for node_set in node_sets:
            subgraph = graph.subgraph(node_set).copy()
            subgraphs.append(subgraph)
            
        return subgraphs

def create_graph_tensors(graph_file: str, time_series_file: str, output_dir: str):
    """
    Create graph tensors for GNN model training.
    
    Args:
        graph_file: Path to road network data
        time_series_file: Path to time series data
        output_dir: Output directory for graph tensors
    """
    builder = GraphBuilder()
    
    # Load data
    try:
        road_segments = pd.read_csv(graph_file)
        time_series_df = pd.read_csv(time_series_file)
        time_series_df['time_bin'] = pd.to_datetime(time_series_df['time_bin'])
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    # Build spatial graph
    spatial_graph = builder.build_spatial_graph(road_segments)
    
    # Create adjacency matrix
    node_list = list(spatial_graph.nodes())
    adj_matrix = builder.create_adjacency_matrix(spatial_graph, node_list)
    
    # Add self-loops and normalize
    adj_matrix = builder.add_self_loops(adj_matrix)
    adj_matrix_norm = builder.normalize_adjacency(adj_matrix, method='symmetric')
    
    # Save graph tensors
    np.save(f"{output_dir}/adjacency_matrix.npy", adj_matrix)
    np.save(f"{output_dir}/adjacency_matrix_normalized.npy", adj_matrix_norm)
    
    # Save node mapping
    node_mapping = {node: idx for idx, node in enumerate(node_list)}
    
    import json
    with open(f"{output_dir}/node_mapping.json", 'w') as f:
        json.dump(node_mapping, f, default=str, indent=2)
    
    # Graph statistics
    stats = {
        'n_nodes': len(node_list),
        'n_edges': spatial_graph.number_of_edges(),
        'avg_degree': np.mean(np.sum(adj_matrix > 0, axis=1)),
        'density': nx.density(spatial_graph)
    }
    
    with open(f"{output_dir}/graph_stats.json", 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"Graph tensors created: {stats}")
    print(f"  Adjacency matrix shape: {adj_matrix.shape}")
    print(f"  Files saved to {output_dir}")

if __name__ == "__main__":
    # Example usage with sample data
    builder = GraphBuilder()
    
    # Create sample road segments
    n_segments = 50
    sample_segments = pd.DataFrame({
        'osm_id': [f'road_{i}' for i in range(n_segments)],
        'avg_lat': np.random.uniform(13.7, 13.8, n_segments),
        'avg_lon': np.random.uniform(100.5, 100.6, n_segments),
        'highway': ['primary'] * n_segments
    })
    
    # Build spatial graph
    spatial_graph = builder.build_spatial_graph(sample_segments)
    adj_matrix = builder.create_adjacency_matrix(spatial_graph)
    adj_matrix_norm = builder.normalize_adjacency(
        builder.add_self_loops(adj_matrix)
    )
    
    print(f"Sample graph created:")
    print(f"  Nodes: {spatial_graph.number_of_nodes()}")
    print(f"  Edges: {spatial_graph.number_of_edges()}")
    print(f"  Adjacency matrix shape: {adj_matrix.shape}")
