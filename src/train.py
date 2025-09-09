"""
Training script for GNN traffic prediction models.
Handles model training, validation, and checkpointing.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
import pandas as pd
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import argparse

# Local imports (will work when packages are installed)
try:
    from models import create_model
    from datasets import create_data_loaders, SpatialTemporalDataset
except ImportError:
    print("Warning: Local modules not found. Install required packages first.")

class TrafficPredictor:
    """Main class for training traffic prediction models."""
    
    def __init__(self, config: Dict):
        """
        Initialize the predictor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Setup logging
        self.setup_logging()
        
        # Initialize model, optimizer, loss function
        self.model = None
        self.optimizer = None
        self.criterion = None
        self.scheduler = None
        
        # Training state
        self.epoch = 0
        self.best_val_loss = float('inf')
        self.train_losses = []
        self.val_losses = []
        
    def setup_logging(self):
        """Setup logging configuration."""
        log_dir = Path(self.config['output_dir']) / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'training.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def build_model(self):
        """Build and initialize the model."""
        self.logger.info(f"Building {self.config['model_type']} model...")
        
        self.model = create_model(self.config['model_type'], self.config)
        self.model.to(self.device)
        
        # Count parameters
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        
        self.logger.info(f"Model created with {total_params:,} total parameters")
        self.logger.info(f"Trainable parameters: {trainable_params:,}")
        
    def setup_optimizer(self):
        """Setup optimizer and learning rate scheduler."""
        optimizer_config = self.config['optimizer']
        
        if optimizer_config['type'] == 'adam':
            self.optimizer = optim.Adam(
                self.model.parameters(),
                lr=optimizer_config['learning_rate'],
                weight_decay=optimizer_config.get('weight_decay', 0.0)
            )
        elif optimizer_config['type'] == 'adamw':
            self.optimizer = optim.AdamW(
                self.model.parameters(),
                lr=optimizer_config['learning_rate'],
                weight_decay=optimizer_config.get('weight_decay', 0.01)
            )
        else:
            raise ValueError(f"Unknown optimizer: {optimizer_config['type']}")
        
        # Learning rate scheduler
        if 'scheduler' in self.config:
            sched_config = self.config['scheduler']
            if sched_config['type'] == 'step':
                self.scheduler = optim.lr_scheduler.StepLR(
                    self.optimizer,
                    step_size=sched_config['step_size'],
                    gamma=sched_config['gamma']
                )
            elif sched_config['type'] == 'cosine':
                self.scheduler = optim.lr_scheduler.CosineAnnealingLR(
                    self.optimizer,
                    T_max=self.config['num_epochs']
                )
    
    def setup_loss_function(self):
        """Setup loss function."""
        loss_config = self.config.get('loss', {'type': 'mse'})
        
        if loss_config['type'] == 'mse':
            self.criterion = nn.MSELoss()
        elif loss_config['type'] == 'mae':
            self.criterion = nn.L1Loss()
        elif loss_config['type'] == 'huber':
            self.criterion = nn.SmoothL1Loss()
        else:
            raise ValueError(f"Unknown loss function: {loss_config['type']}")
    
    def load_data(self) -> Tuple[DataLoader, DataLoader, DataLoader]:
        """Load and create data loaders."""
        self.logger.info("Loading data...")
        
        train_loader, val_loader, test_loader = create_data_loaders(
            data_dir=self.config['data_dir'],
            batch_size=self.config['batch_size'],
            num_workers=self.config.get('num_workers', 0)
        )
        
        self.logger.info(f"Data loaded:")
        self.logger.info(f"  Train batches: {len(train_loader)}")
        self.logger.info(f"  Val batches: {len(val_loader)}")
        self.logger.info(f"  Test batches: {len(test_loader)}")
        
        return train_loader, val_loader, test_loader
    
    def train_epoch(self, train_loader: DataLoader, adjacency_matrix: torch.Tensor) -> float:
        """Train for one epoch."""
        self.model.train()
        total_loss = 0.0
        num_batches = 0
        
        for batch in train_loader:
            # Move to device
            if isinstance(batch, dict):
                sequences = batch['sequence'].to(self.device)
                targets = batch['target'].to(self.device)
            else:
                sequences, targets = batch[0].to(self.device), batch[1].to(self.device)
            
            # Zero gradients
            self.optimizer.zero_grad()
            
            # Forward pass
            predictions = self.model(sequences, adjacency_matrix)
            
            # Calculate loss
            loss = self.criterion(predictions, targets)
            
            # Backward pass
            loss.backward()
            
            # Gradient clipping
            if 'grad_clip' in self.config:
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(), 
                    self.config['grad_clip']
                )
            
            # Update weights
            self.optimizer.step()
            
            total_loss += loss.item()
            num_batches += 1
        
        return total_loss / num_batches if num_batches > 0 else 0.0
    
    def validate(self, val_loader: DataLoader, adjacency_matrix: torch.Tensor) -> float:
        """Validate the model."""
        self.model.eval()
        total_loss = 0.0
        num_batches = 0
        
        with torch.no_grad():
            for batch in val_loader:
                # Move to device
                if isinstance(batch, dict):
                    sequences = batch['sequence'].to(self.device)
                    targets = batch['target'].to(self.device)
                else:
                    sequences, targets = batch[0].to(self.device), batch[1].to(self.device)
                
                # Forward pass
                predictions = self.model(sequences, adjacency_matrix)
                
                # Calculate loss
                loss = self.criterion(predictions, targets)
                
                total_loss += loss.item()
                num_batches += 1
        
        return total_loss / num_batches if num_batches > 0 else float('inf')
    
    def save_checkpoint(self, filepath: str, is_best: bool = False):
        """Save model checkpoint."""
        checkpoint = {
            'epoch': self.epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict() if self.scheduler else None,
            'best_val_loss': self.best_val_loss,
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'config': self.config
        }
        
        torch.save(checkpoint, filepath)
        
        if is_best:
            best_filepath = str(filepath).replace('.pth', '_best.pth')
            torch.save(checkpoint, best_filepath)
    
    def load_checkpoint(self, filepath: str):
        """Load model checkpoint."""
        checkpoint = torch.load(filepath, map_location=self.device)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        if self.scheduler and checkpoint['scheduler_state_dict']:
            self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        
        self.epoch = checkpoint['epoch']
        self.best_val_loss = checkpoint['best_val_loss']
        self.train_losses = checkpoint['train_losses']
        self.val_losses = checkpoint['val_losses']
        
        self.logger.info(f"Checkpoint loaded from {filepath}")
    
    def train(self):
        """Main training loop."""
        self.logger.info("Starting training...")
        
        # Build model and setup training
        self.build_model()
        self.setup_optimizer()
        self.setup_loss_function()
        
        # Load data
        train_loader, val_loader, test_loader = self.load_data()
        
        # Load adjacency matrix
        adj_path = Path(self.config['data_dir']) / 'adjacency_matrix_normalized.npy'
        adjacency_matrix = torch.FloatTensor(np.load(adj_path)).to(self.device)
        
        # Create output directory
        output_dir = Path(self.config['output_dir'])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Training loop
        for epoch in range(self.config['num_epochs']):
            self.epoch = epoch
            
            # Train
            train_loss = self.train_epoch(train_loader, adjacency_matrix)
            self.train_losses.append(train_loss)
            
            # Validate
            val_loss = self.validate(val_loader, adjacency_matrix)
            self.val_losses.append(val_loss)
            
            # Update learning rate
            if self.scheduler:
                self.scheduler.step()
            
            # Log progress
            self.logger.info(
                f"Epoch {epoch+1}/{self.config['num_epochs']} - "
                f"Train Loss: {train_loss:.6f}, Val Loss: {val_loss:.6f}"
            )
            
            # Save checkpoint
            is_best = val_loss < self.best_val_loss
            if is_best:
                self.best_val_loss = val_loss
            
            if (epoch + 1) % self.config.get('save_every', 10) == 0:
                checkpoint_path = output_dir / f"checkpoint_epoch_{epoch+1}.pth"
                self.save_checkpoint(str(checkpoint_path), is_best)
        
        # Final evaluation
        test_loss = self.validate(test_loader, adjacency_matrix)
        self.logger.info(f"Final test loss: {test_loss:.6f}")
        
        # Save final model
        final_path = output_dir / "final_model.pth"
        self.save_checkpoint(str(final_path))
        
        # Save training history
        history = {
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'best_val_loss': self.best_val_loss,
            'test_loss': test_loss
        }
        
        with open(output_dir / 'training_history.json', 'w') as f:
            json.dump(history, f, indent=2)
        
        self.logger.info(f"Training completed. Best validation loss: {self.best_val_loss:.6f}")

def load_config(config_path: str) -> Dict:
    """Load configuration from JSON file."""
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config

def create_default_config() -> Dict:
    """Create default configuration."""
    return {
        "model_type": "temporal_gcn",
        "data_dir": "data/processed",
        "output_dir": "models/experiments",
        "num_epochs": 100,
        "batch_size": 32,
        "num_workers": 0,
        "save_every": 10,
        "grad_clip": 1.0,
        
        # Model parameters
        "num_nodes": 100,
        "input_dim": 10,
        "hidden_dim": 64,
        "output_dim": 1,
        "sequence_length": 12,
        "prediction_horizon": 6,
        
        # Optimizer
        "optimizer": {
            "type": "adamw",
            "learning_rate": 0.001,
            "weight_decay": 0.01
        },
        
        # Scheduler
        "scheduler": {
            "type": "cosine"
        },
        
        # Loss function
        "loss": {
            "type": "mse"
        }
    }

def main():
    """Main training function."""
    parser = argparse.ArgumentParser(description='Train GNN traffic prediction model')
    parser.add_argument('--config', type=str, help='Path to config file')
    parser.add_argument('--data-dir', type=str, default='data/processed', 
                       help='Data directory')
    parser.add_argument('--output-dir', type=str, default='models/experiments',
                       help='Output directory')
    parser.add_argument('--epochs', type=int, default=100, help='Number of epochs')
    parser.add_argument('--batch-size', type=int, default=32, help='Batch size')
    parser.add_argument('--lr', type=float, default=0.001, help='Learning rate')
    
    args = parser.parse_args()
    
    # Load or create configuration
    if args.config:
        config = load_config(args.config)
    else:
        config = create_default_config()
        
        # Override with command line arguments
        config['data_dir'] = args.data_dir
        config['output_dir'] = args.output_dir
        config['num_epochs'] = args.epochs
        config['batch_size'] = args.batch_size
        config['optimizer']['learning_rate'] = args.lr
    
    # Create experiment directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    config['output_dir'] = f"{config['output_dir']}/{timestamp}"
    
    # Save config
    output_dir = Path(config['output_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / 'config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    # Start training
    predictor = TrafficPredictor(config)
    predictor.train()

if __name__ == "__main__":
    main()
