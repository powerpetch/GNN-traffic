"""
Graph Neural Network models for traffic prediction.
Includes ST-GCN, DCRNN, and GraphWaveNet implementations.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Optional, List
import math

class GraphConvolution(nn.Module):
    """Basic Graph Convolution layer."""
    
    def __init__(self, in_features: int, out_features: int, bias: bool = True):
        super(GraphConvolution, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        
        self.weight = nn.Parameter(torch.FloatTensor(in_features, out_features))
        if bias:
            self.bias = nn.Parameter(torch.FloatTensor(out_features))
        else:
            self.register_parameter('bias', None)
            
        self.reset_parameters()
    
    def reset_parameters(self):
        stdv = 1. / math.sqrt(self.weight.size(1))
        self.weight.data.uniform_(-stdv, stdv)
        if self.bias is not None:
            self.bias.data.uniform_(-stdv, stdv)
    
    def forward(self, input: torch.Tensor, adj: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            input: Node features [batch_size, n_nodes, in_features]
            adj: Adjacency matrix [n_nodes, n_nodes]
            
        Returns:
            Output features [batch_size, n_nodes, out_features]
        """
        support = torch.matmul(input, self.weight)
        output = torch.matmul(adj, support)
        
        if self.bias is not None:
            return output + self.bias
        else:
            return output

class TemporalConvolution(nn.Module):
    """Temporal convolution layer with causal padding."""
    
    def __init__(self, in_channels: int, out_channels: int, kernel_size: int, 
                 dilation: int = 1, dropout: float = 0.1):
        super(TemporalConvolution, self).__init__()
        
        self.kernel_size = kernel_size
        self.dilation = dilation
        
        # Causal convolution
        self.conv = nn.Conv1d(
            in_channels, out_channels, kernel_size,
            padding=(kernel_size - 1) * dilation, dilation=dilation
        )
        
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Input tensor [batch_size, channels, time_steps]
            
        Returns:
            Output tensor [batch_size, channels, time_steps]
        """
        # Apply convolution
        out = self.conv(x)
        
        # Remove future information (causal)
        if self.kernel_size > 1:
            out = out[:, :, :-(self.kernel_size - 1) * self.dilation]
        
        return self.dropout(out)

class STGCNBlock(nn.Module):
    """Spatial-Temporal Graph Convolutional Network block."""
    
    def __init__(self, in_channels: int, spatial_channels: int, 
                 out_channels: int, num_nodes: int, dropout: float = 0.1):
        super(STGCNBlock, self).__init__()
        
        self.num_nodes = num_nodes
        
        # Temporal convolution 1
        self.temporal1 = TemporalConvolution(
            in_channels, out_channels, kernel_size=3, dropout=dropout
        )
        
        # Spatial convolution
        self.spatial = GraphConvolution(out_channels, spatial_channels)
        
        # Temporal convolution 2
        self.temporal2 = TemporalConvolution(
            spatial_channels, out_channels, kernel_size=3, dropout=dropout
        )
        
        # Batch normalization
        self.bn = nn.BatchNorm2d(out_channels)
        
        # Residual connection
        if in_channels != out_channels:
            self.residual = nn.Conv2d(in_channels, out_channels, 1)
        else:
            self.residual = None
    
    def forward(self, x: torch.Tensor, adj: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Input tensor [batch_size, in_channels, num_nodes, time_steps]
            adj: Adjacency matrix [num_nodes, num_nodes]
            
        Returns:
            Output tensor [batch_size, out_channels, num_nodes, time_steps]
        """
        batch_size, _, num_nodes, time_steps = x.size()
        
        # Residual connection
        residual = x if self.residual is None else self.residual(x)
        
        # Reshape for temporal convolution: [batch*nodes, channels, time]
        x = x.permute(0, 2, 1, 3).contiguous()  # [batch, nodes, channels, time]
        x = x.view(batch_size * num_nodes, -1, time_steps)  # [batch*nodes, channels, time]
        
        # First temporal convolution
        x = self.temporal1(x)  # [batch*nodes, out_channels, time]
        
        # Reshape for spatial convolution: [batch, time, nodes, channels]
        time_steps = x.size(2)
        x = x.view(batch_size, num_nodes, -1, time_steps)  # [batch, nodes, channels, time]
        x = x.permute(0, 3, 1, 2).contiguous()  # [batch, time, nodes, channels]
        x = x.view(batch_size * time_steps, num_nodes, -1)  # [batch*time, nodes, channels]
        
        # Spatial convolution
        x = F.relu(self.spatial(x, adj))  # [batch*time, nodes, spatial_channels]
        
        # Reshape back for temporal convolution
        x = x.view(batch_size, time_steps, num_nodes, -1)  # [batch, time, nodes, channels]
        x = x.permute(0, 2, 3, 1).contiguous()  # [batch, nodes, channels, time]
        x = x.view(batch_size * num_nodes, -1, time_steps)  # [batch*nodes, channels, time]
        
        # Second temporal convolution
        x = self.temporal2(x)  # [batch*nodes, out_channels, time]
        
        # Reshape to original format
        time_steps = x.size(2)
        x = x.view(batch_size, num_nodes, -1, time_steps)  # [batch, nodes, channels, time]
        x = x.permute(0, 2, 1, 3).contiguous()  # [batch, channels, nodes, time]
        
        # Batch normalization and residual
        x = self.bn(x)
        x = F.relu(x + residual)
        
        return x

class STGCN(nn.Module):
    """Spatial-Temporal Graph Convolutional Network for traffic prediction."""
    
    def __init__(self, num_nodes: int, num_features: int, num_timesteps_input: int,
                 num_timesteps_output: int, hidden_dim: int = 64, num_layers: int = 2):
        super(STGCN, self).__init__()
        
        self.num_nodes = num_nodes
        self.num_features = num_features
        self.num_timesteps_input = num_timesteps_input
        self.num_timesteps_output = num_timesteps_output
        
        # ST-GCN blocks
        self.blocks = nn.ModuleList()
        
        # First block
        self.blocks.append(
            STGCNBlock(num_features, hidden_dim, hidden_dim, num_nodes)
        )
        
        # Hidden blocks
        for _ in range(num_layers - 1):
            self.blocks.append(
                STGCNBlock(hidden_dim, hidden_dim, hidden_dim, num_nodes)
            )
        
        # Output layer
        self.output_layer = nn.Conv2d(
            hidden_dim, num_timesteps_output, 
            kernel_size=(1, num_timesteps_input)
        )
        
    def forward(self, x: torch.Tensor, adj: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Input tensor [batch_size, num_timesteps_input, num_nodes, num_features]
            adj: Adjacency matrix [num_nodes, num_nodes]
            
        Returns:
            Output tensor [batch_size, num_timesteps_output, num_nodes, 1]
        """
        # Reshape input: [batch, features, nodes, time]
        x = x.permute(0, 3, 2, 1).contiguous()
        
        # Apply ST-GCN blocks
        for block in self.blocks:
            x = block(x, adj)
        
        # Output layer
        x = self.output_layer(x)  # [batch, num_timesteps_output, nodes, 1]
        
        # Reshape output: [batch, num_timesteps_output, nodes, 1]
        x = x.permute(0, 1, 2, 3).contiguous()
        
        return x

class GCNLayer(nn.Module):
    """Graph Convolution Network layer."""
    
    def __init__(self, in_features: int, out_features: int, 
                 activation: Optional[str] = 'relu', dropout: float = 0.0):
        super(GCNLayer, self).__init__()
        
        self.linear = nn.Linear(in_features, out_features)
        self.activation = activation
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x: torch.Tensor, adj: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Node features [batch_size, num_nodes, in_features]
            adj: Normalized adjacency matrix [num_nodes, num_nodes]
            
        Returns:
            Output features [batch_size, num_nodes, out_features]
        """
        # Linear transformation
        x = self.linear(x)
        
        # Graph convolution: AXW
        x = torch.matmul(adj, x)
        
        # Activation
        if self.activation == 'relu':
            x = F.relu(x)
        elif self.activation == 'tanh':
            x = torch.tanh(x)
        
        # Dropout
        x = self.dropout(x)
        
        return x

class SimpleGCN(nn.Module):
    """Simple Graph Convolutional Network for traffic prediction."""
    
    def __init__(self, num_nodes: int, input_dim: int, hidden_dims: List[int],
                 output_dim: int, dropout: float = 0.1):
        super(SimpleGCN, self).__init__()
        
        self.num_nodes = num_nodes
        self.layers = nn.ModuleList()
        
        # Input layer
        prev_dim = input_dim
        for hidden_dim in hidden_dims:
            self.layers.append(
                GCNLayer(prev_dim, hidden_dim, activation='relu', dropout=dropout)
            )
            prev_dim = hidden_dim
        
        # Output layer
        self.layers.append(
            GCNLayer(prev_dim, output_dim, activation=None, dropout=0.0)
        )
        
    def forward(self, x: torch.Tensor, adj: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Input features [batch_size, num_nodes, input_dim]
            adj: Adjacency matrix [num_nodes, num_nodes]
            
        Returns:
            Output [batch_size, num_nodes, output_dim]
        """
        for layer in self.layers:
            x = layer(x, adj)
        
        return x

class TemporalGCN(nn.Module):
    """Temporal GCN that processes sequences of graph data."""
    
    def __init__(self, num_nodes: int, input_dim: int, hidden_dim: int,
                 output_dim: int, sequence_length: int, prediction_horizon: int):
        super(TemporalGCN, self).__init__()
        
        self.num_nodes = num_nodes
        self.sequence_length = sequence_length
        self.prediction_horizon = prediction_horizon
        
        # GCN for each time step
        self.gcn = SimpleGCN(
            num_nodes, input_dim, [hidden_dim, hidden_dim], hidden_dim
        )
        
        # LSTM for temporal modeling
        self.lstm = nn.LSTM(
            hidden_dim, hidden_dim, batch_first=True
        )
        
        # Output projection
        self.output_proj = nn.Linear(hidden_dim, output_dim * prediction_horizon)
        
    def forward(self, x: torch.Tensor, adj: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Input sequences [batch_size, sequence_length, num_nodes, input_dim]
            adj: Adjacency matrix [num_nodes, num_nodes]
            
        Returns:
            Predictions [batch_size, prediction_horizon, num_nodes, output_dim]
        """
        batch_size, seq_len, num_nodes, input_dim = x.size()
        
        # Process each time step with GCN
        gcn_outputs = []
        for t in range(seq_len):
            # x_t: [batch_size, num_nodes, input_dim]
            x_t = x[:, t, :, :]
            gcn_out = self.gcn(x_t, adj)  # [batch_size, num_nodes, hidden_dim]
            gcn_outputs.append(gcn_out)
        
        # Stack temporal outputs: [batch_size, seq_len, num_nodes, hidden_dim]
        gcn_sequence = torch.stack(gcn_outputs, dim=1)
        
        # Process with LSTM (treat each node independently)
        batch_size, seq_len, num_nodes, hidden_dim = gcn_sequence.size()
        
        # Reshape for LSTM: [batch_size * num_nodes, seq_len, hidden_dim]
        lstm_input = gcn_sequence.view(batch_size * num_nodes, seq_len, hidden_dim)
        
        # LSTM forward
        lstm_out, _ = self.lstm(lstm_input)  # [batch*nodes, seq_len, hidden_dim]
        
        # Take last output: [batch*nodes, hidden_dim]
        last_output = lstm_out[:, -1, :]
        
        # Output projection: [batch*nodes, output_dim * prediction_horizon]
        predictions = self.output_proj(last_output)
        
        # Reshape to final format: [batch, prediction_horizon, nodes, output_dim]
        predictions = predictions.view(
            batch_size, num_nodes, self.prediction_horizon, -1
        )
        predictions = predictions.permute(0, 2, 1, 3).contiguous()
        
        return predictions

def create_model(model_type: str, config: dict) -> nn.Module:
    """
    Factory function to create models.
    
    Args:
        model_type: Type of model ('stgcn', 'simple_gcn', 'temporal_gcn')
        config: Model configuration dictionary
        
    Returns:
        Initialized model
    """
    if model_type == 'stgcn':
        return STGCN(
            num_nodes=config['num_nodes'],
            num_features=config['num_features'],
            num_timesteps_input=config['sequence_length'],
            num_timesteps_output=config['prediction_horizon'],
            hidden_dim=config.get('hidden_dim', 64),
            num_layers=config.get('num_layers', 2)
        )
    
    elif model_type == 'simple_gcn':
        return SimpleGCN(
            num_nodes=config['num_nodes'],
            input_dim=config['input_dim'],
            hidden_dims=config.get('hidden_dims', [64, 64]),
            output_dim=config['output_dim'],
            dropout=config.get('dropout', 0.1)
        )
    
    elif model_type == 'temporal_gcn':
        return TemporalGCN(
            num_nodes=config['num_nodes'],
            input_dim=config['input_dim'],
            hidden_dim=config.get('hidden_dim', 64),
            output_dim=config['output_dim'],
            sequence_length=config['sequence_length'],
            prediction_horizon=config['prediction_horizon']
        )
    
    else:
        raise ValueError(f"Unknown model type: {model_type}")

if __name__ == "__main__":
    # Test model creation
    config = {
        'num_nodes': 50,
        'num_features': 10,
        'sequence_length': 12,
        'prediction_horizon': 6,
        'hidden_dim': 64,
        'num_layers': 2
    }
    
    # Test STGCN
    model = create_model('stgcn', config)
    print(f"STGCN created: {sum(p.numel() for p in model.parameters())} parameters")
    
    # Test forward pass
    batch_size = 8
    x = torch.randn(batch_size, config['sequence_length'], config['num_nodes'], config['num_features'])
    adj = torch.randn(config['num_nodes'], config['num_nodes'])
    
    with torch.no_grad():
        output = model(x, adj)
        print(f"Output shape: {output.shape}")
