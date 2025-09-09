"""
Evaluation script for GNN traffic prediction models.
Evaluates trained models and generates performance metrics.
"""

import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Local imports
try:
    from models import create_model
    from datasets import SpatialTemporalDataset
    from train import TrafficPredictor
except ImportError:
    print("Warning: Local modules not found. Install required packages first.")

class ModelEvaluator:
    """Class for evaluating trained traffic prediction models."""
    
    def __init__(self, model_path: str, config_path: str, data_dir: str):
        """
        Initialize evaluator.
        
        Args:
            model_path: Path to trained model checkpoint
            config_path: Path to model configuration
            data_dir: Path to data directory
        """
        self.model_path = model_path
        self.config_path = config_path
        self.data_dir = data_dir
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Load model
        self.model = None
        self.load_model()
        
        # Load adjacency matrix
        adj_path = Path(data_dir) / 'adjacency_matrix_normalized.npy'
        self.adjacency_matrix = torch.FloatTensor(np.load(adj_path)).to(self.device)
        
    def load_model(self):
        """Load the trained model."""
        # Create model
        self.model = create_model(self.config['model_type'], self.config)
        
        # Load checkpoint
        checkpoint = torch.load(self.model_path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.to(self.device)
        self.model.eval()
        
        print(f"Model loaded from {self.model_path}")
    
    def evaluate_dataset(self, dataset: SpatialTemporalDataset) -> Dict:
        """
        Evaluate model on a dataset.
        
        Args:
            dataset: Dataset to evaluate on
            
        Returns:
            Dictionary with evaluation metrics
        """
        predictions = []
        targets = []
        road_ids = []
        
        self.model.eval()
        with torch.no_grad():
            for i in range(len(dataset)):
                sample = dataset[i]
                
                # Get input sequence and target
                sequence = sample['sequence'].unsqueeze(0).to(self.device)  # Add batch dim
                target = sample['target'].unsqueeze(0).to(self.device)
                road_id = sample['road_id']
                
                # Predict
                prediction = self.model(sequence, self.adjacency_matrix)
                
                # Store results
                predictions.append(prediction.cpu().numpy())
                targets.append(target.cpu().numpy())
                road_ids.append(road_id)
        
        # Convert to numpy arrays
        predictions = np.concatenate(predictions, axis=0)
        targets = np.concatenate(targets, axis=0)
        
        # Calculate metrics
        metrics = self.calculate_metrics(predictions, targets)
        
        return {
            'metrics': metrics,
            'predictions': predictions,
            'targets': targets,
            'road_ids': road_ids
        }
    
    def calculate_metrics(self, predictions: np.ndarray, targets: np.ndarray) -> Dict:
        """
        Calculate evaluation metrics.
        
        Args:
            predictions: Model predictions
            targets: Ground truth targets
            
        Returns:
            Dictionary with metrics
        """
        # Flatten arrays for metric calculation
        pred_flat = predictions.flatten()
        target_flat = targets.flatten()
        
        # Remove any NaN values
        mask = ~(np.isnan(pred_flat) | np.isnan(target_flat))
        pred_clean = pred_flat[mask]
        target_clean = target_flat[mask]
        
        if len(pred_clean) == 0:
            return {'error': 'No valid predictions'}
        
        # Calculate metrics
        mae = mean_absolute_error(target_clean, pred_clean)
        mse = mean_squared_error(target_clean, pred_clean)
        rmse = np.sqrt(mse)
        
        # MAPE (Mean Absolute Percentage Error)
        mask_nonzero = target_clean != 0
        if np.sum(mask_nonzero) > 0:
            mape = np.mean(np.abs((target_clean[mask_nonzero] - pred_clean[mask_nonzero]) / 
                                target_clean[mask_nonzero])) * 100
        else:
            mape = float('inf')
        
        # R-squared
        r2 = r2_score(target_clean, pred_clean)
        
        # Additional traffic-specific metrics
        # Mean speed error
        mean_speed_error = np.mean(target_clean - pred_clean)
        
        # Accuracy within threshold (e.g., ±5 km/h for speed)
        threshold = 5.0
        accuracy_threshold = np.mean(np.abs(target_clean - pred_clean) <= threshold) * 100
        
        return {
            'mae': float(mae),
            'mse': float(mse),
            'rmse': float(rmse),
            'mape': float(mape),
            'r2': float(r2),
            'mean_speed_error': float(mean_speed_error),
            'accuracy_5kmh': float(accuracy_threshold),
            'num_samples': len(pred_clean)
        }
    
    def evaluate_by_time(self, results: Dict) -> Dict:
        """
        Evaluate performance by time of day and day of week.
        
        Args:
            results: Results from evaluate_dataset
            
        Returns:
            Time-based evaluation metrics
        """
        predictions = results['predictions']
        targets = results['targets']
        
        # Load test dataset to get timestamps
        test_dataset = SpatialTemporalDataset(self.data_dir, 'test')
        
        time_metrics = {}
        
        # Evaluate by hour of day
        hourly_metrics = {}
        for hour in range(24):
            # This is simplified - in practice, you'd need to track timestamps
            # through the evaluation process
            hourly_metrics[hour] = {'mae': 0.0, 'rmse': 0.0}  # Placeholder
        
        time_metrics['hourly'] = hourly_metrics
        
        # Evaluate by day of week
        daily_metrics = {}
        for day in range(7):
            daily_metrics[day] = {'mae': 0.0, 'rmse': 0.0}  # Placeholder
        
        time_metrics['daily'] = daily_metrics
        
        return time_metrics
    
    def evaluate_by_road_type(self, results: Dict) -> Dict:
        """
        Evaluate performance by road type/characteristics.
        
        Args:
            results: Results from evaluate_dataset
            
        Returns:
            Road-type-based evaluation metrics
        """
        # This would require road metadata
        # Placeholder implementation
        road_type_metrics = {
            'highway': {'mae': 0.0, 'rmse': 0.0},
            'arterial': {'mae': 0.0, 'rmse': 0.0},
            'local': {'mae': 0.0, 'rmse': 0.0}
        }
        
        return road_type_metrics
    
    def generate_visualizations(self, results: Dict, output_dir: str):
        """
        Generate evaluation visualizations.
        
        Args:
            results: Evaluation results
            output_dir: Directory to save plots
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        predictions = results['predictions']
        targets = results['targets']
        
        # Flatten for plotting
        pred_flat = predictions.flatten()
        target_flat = targets.flatten()
        
        # Remove NaN values
        mask = ~(np.isnan(pred_flat) | np.isnan(target_flat))
        pred_clean = pred_flat[mask]
        target_clean = target_flat[mask]
        
        # 1. Scatter plot: Predicted vs Actual
        plt.figure(figsize=(10, 8))
        plt.scatter(target_clean, pred_clean, alpha=0.5, s=1)
        plt.plot([target_clean.min(), target_clean.max()], 
                [target_clean.min(), target_clean.max()], 'r--', lw=2)
        plt.xlabel('Actual Speed (km/h)')
        plt.ylabel('Predicted Speed (km/h)')
        plt.title('Predicted vs Actual Speed')
        plt.grid(True, alpha=0.3)
        
        # Add R² to plot
        r2 = results['metrics']['r2']
        plt.text(0.05, 0.95, f'R² = {r2:.3f}', transform=plt.gca().transAxes, 
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig(output_path / 'predicted_vs_actual.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Residual plot
        residuals = pred_clean - target_clean
        
        plt.figure(figsize=(10, 6))
        plt.scatter(target_clean, residuals, alpha=0.5, s=1)
        plt.axhline(y=0, color='r', linestyle='--')
        plt.xlabel('Actual Speed (km/h)')
        plt.ylabel('Residuals (Predicted - Actual)')
        plt.title('Residual Plot')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path / 'residuals.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Error distribution
        plt.figure(figsize=(10, 6))
        plt.hist(residuals, bins=50, alpha=0.7, edgecolor='black')
        plt.xlabel('Prediction Error (km/h)')
        plt.ylabel('Frequency')
        plt.title('Distribution of Prediction Errors')
        plt.axvline(x=0, color='r', linestyle='--')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path / 'error_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 4. Time series plot (sample)
        if len(predictions) > 0:
            # Plot first few sequences
            n_samples = min(5, len(predictions))
            
            plt.figure(figsize=(15, 10))
            for i in range(n_samples):
                plt.subplot(n_samples, 1, i+1)
                
                # Get sequence (assuming shape is [batch, time, nodes, features])
                if len(predictions.shape) >= 2:
                    pred_seq = predictions[i].flatten()
                    target_seq = targets[i].flatten()
                    
                    time_steps = range(len(pred_seq))
                    plt.plot(time_steps, target_seq, 'b-', label='Actual', linewidth=2)
                    plt.plot(time_steps, pred_seq, 'r--', label='Predicted', linewidth=2)
                    
                    plt.ylabel('Speed (km/h)')
                    plt.title(f'Sample {i+1}: Traffic Speed Prediction')
                    plt.legend()
                    plt.grid(True, alpha=0.3)
            
            plt.xlabel('Time Step')
            plt.tight_layout()
            plt.savefig(output_path / 'time_series_samples.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        print(f"Visualizations saved to {output_path}")
    
    def run_full_evaluation(self, output_dir: str):
        """
        Run complete evaluation and save results.
        
        Args:
            output_dir: Directory to save evaluation results
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print("Starting model evaluation...")
        
        # Evaluate on test set
        test_dataset = SpatialTemporalDataset(self.data_dir, 'test')
        test_results = self.evaluate_dataset(test_dataset)
        
        print(f"Test set evaluation completed:")
        print(f"  MAE: {test_results['metrics']['mae']:.4f}")
        print(f"  RMSE: {test_results['metrics']['rmse']:.4f}")
        print(f"  MAPE: {test_results['metrics']['mape']:.2f}%")
        print(f"  R²: {test_results['metrics']['r2']:.4f}")
        
        # Time-based evaluation
        time_metrics = self.evaluate_by_time(test_results)
        
        # Road-type evaluation
        road_metrics = self.evaluate_by_road_type(test_results)
        
        # Generate visualizations
        self.generate_visualizations(test_results, str(output_path / 'plots'))
        
        # Save results
        evaluation_results = {
            'test_metrics': test_results['metrics'],
            'time_based_metrics': time_metrics,
            'road_type_metrics': road_metrics,
            'config': self.config,
            'model_path': self.model_path
        }
        
        with open(output_path / 'evaluation_results.json', 'w') as f:
            json.dump(evaluation_results, f, indent=2)
        
        # Save detailed predictions for further analysis
        np.save(output_path / 'predictions.npy', test_results['predictions'])
        np.save(output_path / 'targets.npy', test_results['targets'])
        
        with open(output_path / 'road_ids.json', 'w') as f:
            json.dump(test_results['road_ids'], f)
        
        print(f"Evaluation completed. Results saved to {output_path}")
        
        return evaluation_results

def compare_models(model_paths: List[str], data_dir: str, output_dir: str):
    """
    Compare multiple trained models.
    
    Args:
        model_paths: List of paths to model checkpoints
        data_dir: Path to data directory
        output_dir: Directory to save comparison results
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    for i, model_path in enumerate(model_paths):
        model_name = f"model_{i+1}"
        config_path = str(Path(model_path).parent / 'config.json')
        
        try:
            evaluator = ModelEvaluator(model_path, config_path, data_dir)
            test_dataset = SpatialTemporalDataset(data_dir, 'test')
            model_results = evaluator.evaluate_dataset(test_dataset)
            
            results[model_name] = {
                'path': model_path,
                'metrics': model_results['metrics']
            }
            
            print(f"{model_name}: MAE={model_results['metrics']['mae']:.4f}, "
                  f"RMSE={model_results['metrics']['rmse']:.4f}")
            
        except Exception as e:
            print(f"Error evaluating {model_path}: {e}")
    
    # Save comparison results
    with open(output_path / 'model_comparison.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Model comparison saved to {output_path}")

def main():
    """Main evaluation function."""
    parser = argparse.ArgumentParser(description='Evaluate GNN traffic prediction model')
    parser.add_argument('--model', type=str, required=True, 
                       help='Path to model checkpoint')
    parser.add_argument('--config', type=str, 
                       help='Path to config file (if different from model dir)')
    parser.add_argument('--data-dir', type=str, default='data/processed',
                       help='Data directory')
    parser.add_argument('--output-dir', type=str, default='evaluation_results',
                       help='Output directory for results')
    parser.add_argument('--compare', nargs='+', 
                       help='Compare multiple models (provide multiple paths)')
    
    args = parser.parse_args()
    
    if args.compare:
        # Compare multiple models
        compare_models(args.compare, args.data_dir, args.output_dir)
    else:
        # Evaluate single model
        if args.config:
            config_path = args.config
        else:
            config_path = str(Path(args.model).parent / 'config.json')
        
        evaluator = ModelEvaluator(args.model, config_path, args.data_dir)
        evaluator.run_full_evaluation(args.output_dir)

if __name__ == "__main__":
    main()
