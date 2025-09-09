"""
Dataset creation module for GNN traffic prediction.
Creates PyTorch datasets with windowed sequences and graph structure.
"""

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from typing import Tuple, Dict, List, Optional
import json
import logging

class TrafficDataset(Dataset):
    """PyTorch Dataset for traffic prediction with graph structure."""
    
    def __init__(self, sequences: np.ndarray, targets: np.ndarray, 
                 adjacency_matrix: np.ndarray, road_ids: List[str],
                 node_mapping: Dict[str, int]):
        """
        Initialize traffic dataset.
        
        Args:
            sequences: Input sequences [batch_size, seq_len, n_features]
            targets: Target sequences [batch_size, pred_len, n_features]
            adjacency_matrix: Graph adjacency matrix [n_nodes, n_nodes]
            road_ids: List of road IDs for each sequence
            node_mapping: Mapping from road_id to node index
        """
        self.sequences = torch.FloatTensor(sequences)
        self.targets = torch.FloatTensor(targets)
        self.adjacency_matrix = torch.FloatTensor(adjacency_matrix)
        self.road_ids = road_ids
        self.node_mapping = node_mapping
        
        # Create node indices for each sequence
        self.node_indices = []
        for road_id in road_ids:
            if road_id in node_mapping:
                self.node_indices.append(node_mapping[road_id])
            else:
                self.node_indices.append(0)  # Default to first node
        
        self.node_indices = torch.LongTensor(self.node_indices)
        
    def __len__(self) -> int:
        return len(self.sequences)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, int]:
        """
        Get a single sample.
        
        Returns:
            Tuple of (sequence, target, adjacency_matrix, node_index)
        """
        return (
            self.sequences[idx],
            self.targets[idx], 
            self.adjacency_matrix,
            self.node_indices[idx]
        )

class SpatialTemporalDataset(Dataset):
    """Dataset for spatial-temporal GNN with multiple road segments."""
    
    def __init__(self, data_dir: str, split: str = 'train'):
        """
        Initialize spatial-temporal dataset.
        
        Args:
            data_dir: Directory containing processed data
            split: Data split ('train', 'test', 'val')
        """
        self.data_dir = data_dir
        self.split = split
        
        # Load data
        self.sequences = np.load(f"{data_dir}/X_{split}.npy")
        self.targets = np.load(f"{data_dir}/y_{split}.npy")
        
        # Load graph structure
        self.adjacency_matrix = np.load(f"{data_dir}/adjacency_matrix_normalized.npy")
        
        # Load metadata
        with open(f"{data_dir}/metadata.json", 'r') as f:
            self.metadata = json.load(f)
            
        with open(f"{data_dir}/node_mapping.json", 'r') as f:
            self.node_mapping = json.load(f)
        
        # Get road IDs for this split
        road_ids_key = f"{split}_road_ids"
        self.road_ids = self.metadata.get(road_ids_key, [])
        
        # Convert to tensors
        self.sequences = torch.FloatTensor(self.sequences)
        self.targets = torch.FloatTensor(self.targets)
        self.adjacency_matrix = torch.FloatTensor(self.adjacency_matrix)
        
        # Create node index mapping for batches
        self.create_node_indices()
        
    def create_node_indices(self):
        """Create node indices for graph operations."""
        self.node_indices = []
        
        for road_id in self.road_ids:
            if str(road_id) in self.node_mapping:
                node_idx = self.node_mapping[str(road_id)]
                self.node_indices.append(node_idx)
            else:
                self.node_indices.append(0)  # Default node
        
        self.node_indices = torch.LongTensor(self.node_indices)
        
    def __len__(self) -> int:
        return len(self.sequences)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """
        Get a single sample with all necessary tensors.
        
        Returns:
            Dictionary with sequences, targets, adjacency matrix, and node info
        """
        return {
            'sequence': self.sequences[idx],
            'target': self.targets[idx],
            'adjacency': self.adjacency_matrix,
            'node_idx': self.node_indices[idx] if idx < len(self.node_indices) else 0,
            'road_id': self.road_ids[idx] if idx < len(self.road_ids) else 'unknown'
        }

class GraphBatchDataset(Dataset):
    """Dataset that creates graph batches for efficient GNN training."""
    
    def __init__(self, data_dir: str, split: str = 'train', 
                 batch_size: int = 32, max_nodes_per_batch: int = 100):
        """
        Initialize graph batch dataset.
        
        Args:
            data_dir: Directory containing processed data
            split: Data split
            batch_size: Number of sequences per batch
            max_nodes_per_batch: Maximum nodes to include in each batch
        """
        self.data_dir = data_dir
        self.split = split
        self.batch_size = batch_size
        self.max_nodes_per_batch = max_nodes_per_batch
        
        # Load base dataset
        self.base_dataset = SpatialTemporalDataset(data_dir, split)
        
        # Create batches
        self.create_batches()
        
    def create_batches(self):
        """Pre-create batches for efficient loading."""
        self.batches = []
        n_samples = len(self.base_dataset)
        
        for i in range(0, n_samples, self.batch_size):
            end_idx = min(i + self.batch_size, n_samples)
            batch_indices = list(range(i, end_idx))
            
            # Get unique nodes in this batch
            batch_road_ids = set()
            for idx in batch_indices:
                road_id = self.base_dataset.road_ids[idx]
                batch_road_ids.add(road_id)
            
            # Limit nodes per batch
            if len(batch_road_ids) > self.max_nodes_per_batch:
                batch_road_ids = list(batch_road_ids)[:self.max_nodes_per_batch]
            
            # Create subgraph for this batch
            node_indices = [self.base_dataset.node_mapping[str(rid)] 
                          for rid in batch_road_ids 
                          if str(rid) in self.base_dataset.node_mapping]
            
            if node_indices:
                subgraph_adj = self.base_dataset.adjacency_matrix[node_indices][:, node_indices]
                
                batch_info = {
                    'indices': batch_indices,
                    'road_ids': list(batch_road_ids),
                    'node_indices': node_indices,
                    'subgraph_adj': subgraph_adj
                }
                
                self.batches.append(batch_info)
    
    def __len__(self) -> int:
        return len(self.batches)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """
        Get a pre-created batch.
        
        Returns:
            Dictionary with batch sequences, targets, and subgraph
        """
        batch_info = self.batches[idx]
        
        # Collect sequences and targets for this batch
        sequences = []
        targets = []
        node_features = []
        
        for sample_idx in batch_info['indices']:
            sample = self.base_dataset[sample_idx]
            sequences.append(sample['sequence'])
            targets.append(sample['target'])
            
        return {
            'sequences': torch.stack(sequences),
            'targets': torch.stack(targets),
            'adjacency': batch_info['subgraph_adj'],
            'node_indices': torch.LongTensor(batch_info['node_indices']),
            'road_ids': batch_info['road_ids']
        }

def create_data_loaders(data_dir: str, batch_size: int = 32, 
                       num_workers: int = 0) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """
    Create data loaders for train, validation, and test sets.
    
    Args:
        data_dir: Directory containing processed data
        batch_size: Batch size for data loaders
        num_workers: Number of worker processes
        
    Returns:
        Tuple of (train_loader, val_loader, test_loader)
    """
    # Create datasets
    train_dataset = SpatialTemporalDataset(data_dir, 'train')
    
    # Create validation set if test data exists
    try:
        test_dataset = SpatialTemporalDataset(data_dir, 'test')
        
        # Split test into val and test (50/50)
        test_size = len(test_dataset)
        val_size = test_size // 2
        
        val_indices = list(range(val_size))
        test_indices = list(range(val_size, test_size))
        
        val_dataset = torch.utils.data.Subset(test_dataset, val_indices)
        test_dataset = torch.utils.data.Subset(test_dataset, test_indices)
        
    except FileNotFoundError:
        # If no test data, split train into train/val (80/20)
        train_size = len(train_dataset)
        val_size = train_size // 5
        train_size = train_size - val_size
        
        train_dataset, val_dataset = torch.utils.data.random_split(
            train_dataset, [train_size, val_size]
        )
        test_dataset = val_dataset  # Use val as test for now
    
    # Create data loaders
    train_loader = DataLoader(
        train_dataset, 
        batch_size=batch_size, 
        shuffle=True, 
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available()
    )
    
    val_loader = DataLoader(
        val_dataset, 
        batch_size=batch_size, 
        shuffle=False, 
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available()
    )
    
    test_loader = DataLoader(
        test_dataset, 
        batch_size=batch_size, 
        shuffle=False, 
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available()
    )
    
    return train_loader, val_loader, test_loader

def collate_graph_batch(batch: List[Dict]) -> Dict[str, torch.Tensor]:
    """
    Custom collate function for graph data.
    
    Args:
        batch: List of samples from dataset
        
    Returns:
        Batched tensors
    """
    # Stack sequences and targets
    sequences = torch.stack([sample['sequence'] for sample in batch])
    targets = torch.stack([sample['target'] for sample in batch])
    
    # Use the adjacency matrix from first sample (should be same for all)
    adjacency = batch[0]['adjacency']
    
    # Collect node indices
    node_indices = torch.stack([sample['node_idx'] for sample in batch])
    
    # Collect road IDs
    road_ids = [sample['road_id'] for sample in batch]
    
    return {
        'sequences': sequences,
        'targets': targets,
        'adjacency': adjacency,
        'node_indices': node_indices,
        'road_ids': road_ids
    }

class WindowDataset(Dataset):
    """Dataset for creating sliding windows from time series data."""
    
    def __init__(self, time_series_df: pd.DataFrame, window_size: int = 12, 
                 prediction_horizon: int = 6, target_features: List[str] = ['avg_speed']):
        """
        Initialize window dataset.
        
        Args:
            time_series_df: Time series DataFrame
            window_size: Size of input window
            prediction_horizon: Number of steps to predict
            target_features: List of features to predict
        """
        self.time_series_df = time_series_df.sort_values(['road_id', 'time_bin'])
        self.window_size = window_size
        self.prediction_horizon = prediction_horizon
        self.target_features = target_features
        
        # Get feature columns (excluding identifiers)
        exclude_cols = ['road_id', 'time_bin']
        self.feature_cols = [col for col in time_series_df.columns 
                           if col not in exclude_cols]
        
        # Create windows
        self.create_windows()
        
    def create_windows(self):
        """Create sliding windows from time series data."""
        self.windows = []
        
        for road_id, group in self.time_series_df.groupby('road_id'):
            if len(group) < self.window_size + self.prediction_horizon:
                continue
                
            features = group[self.feature_cols].values
            targets = group[self.target_features].values
            
            for i in range(len(features) - self.window_size - self.prediction_horizon + 1):
                window = {
                    'features': features[i:i + self.window_size],
                    'targets': targets[i + self.window_size:i + self.window_size + self.prediction_horizon],
                    'road_id': road_id,
                    'start_time': group.iloc[i]['time_bin'],
                    'end_time': group.iloc[i + self.window_size - 1]['time_bin']
                }
                self.windows.append(window)
    
    def __len__(self) -> int:
        return len(self.windows)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """Get a single window."""
        window = self.windows[idx]
        
        return {
            'features': torch.FloatTensor(window['features']),
            'targets': torch.FloatTensor(window['targets']),
            'road_id': window['road_id'],
            'start_time': window['start_time'],
            'end_time': window['end_time']
        }

def test_dataset_creation():
    """Test dataset creation with sample data."""
    # Create sample time series data
    dates = pd.date_range('2024-01-01', periods=1000, freq='5min')
    n_roads = 10
    
    data = []
    for road_idx in range(n_roads):
        for i, date in enumerate(dates):
            data.append({
                'road_id': f'road_{road_idx}',
                'time_bin': date,
                'avg_speed': 50 + 10 * np.sin(i * 0.1) + np.random.normal(0, 5),
                'vehicle_count': max(0, 20 + 5 * np.sin(i * 0.05) + np.random.normal(0, 3)),
                'traffic_density': max(0, 2 + np.sin(i * 0.08) + np.random.normal(0, 0.5)),
                'hour': date.hour,
                'day_of_week': date.dayofweek
            })
    
    df = pd.DataFrame(data)
    
    # Test window dataset
    window_dataset = WindowDataset(df, window_size=12, prediction_horizon=6)
    print(f"Created {len(window_dataset)} windows")
    
    # Test a sample
    sample = window_dataset[0]
    print(f"Sample features shape: {sample['features'].shape}")
    print(f"Sample targets shape: {sample['targets'].shape}")
    
    return window_dataset

if __name__ == "__main__":
    # Test dataset creation
    test_dataset = test_dataset_creation()
    
    # Create a simple data loader
    data_loader = DataLoader(test_dataset, batch_size=8, shuffle=True)
    
    # Test one batch
    for batch in data_loader:
        print("Batch loaded successfully:")
        print(f"  Features: {batch['features'].shape}")
        print(f"  Targets: {batch['targets'].shape}")
        print(f"  Road IDs: {len(batch['road_id'])}")
        break
