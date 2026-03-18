"""
Model Persistence Manager
Handles saving, loading, and versioning of trained ML models
"""
import joblib
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any
import hashlib


class ModelManager:
    """
    Manages ML model persistence, versioning, and metadata
    """
    
    def __init__(self, models_dir: str = 'models'):
        self.models_dir = models_dir
        self.ensure_models_directory()
        self.metadata_file = os.path.join(models_dir, 'model_registry.json')
        self.load_registry()
    
    def ensure_models_directory(self):
        """Create models directory if it doesn't exist"""
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)
            print(f"✅ Created models directory: {self.models_dir}")
    
    def load_registry(self):
        """Load model registry (metadata about saved models)"""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                self.registry = json.load(f)
        else:
            self.registry = {}
    
    def save_registry(self):
        """Save model registry to disk"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def save_model(self, model: Any, model_name: str, 
                   metadata: Optional[Dict] = None,
                   version: Optional[str] = None) -> str:
        """
        Save a trained model with metadata
        
        Args:
            model: Trained sklearn model
            model_name: Name identifier (e.g., 'severity_classifier')
            metadata: Additional info (accuracy, training_date, etc.)
            version: Version string (auto-generated if None)
            
        Returns:
            Path to saved model file
        """
        # Generate version if not provided
        if version is None:
            version = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create filename
        filename = f"{model_name}_v{version}.pkl"
        filepath = os.path.join(self.models_dir, filename)
        
        # Save model using joblib
        joblib.dump(model, filepath)
        
        # Calculate model hash for integrity
        model_hash = self._calculate_file_hash(filepath)
        
        # Store metadata
        model_metadata = {
            'model_name': model_name,
            'version': version,
            'filepath': filepath,
            'filename': filename,
            'saved_at': datetime.now().isoformat(),
            'file_size_mb': os.path.getsize(filepath) / (1024 * 1024),
            'model_hash': model_hash,
            'model_type': str(type(model).__name__)
        }
        
        # Merge with user-provided metadata
        if metadata:
            model_metadata.update(metadata)
        
        # Update registry
        if model_name not in self.registry:
            self.registry[model_name] = []
        
        self.registry[model_name].append(model_metadata)
        self.save_registry()
        
        print(f"✅ Model saved: {filename}")
        print(f"   Size: {model_metadata['file_size_mb']:.2f} MB")
        print(f"   Type: {model_metadata['model_type']}")
        
        return filepath
    
    def load_model(self, model_name: str, version: Optional[str] = None) -> Any:
        """
        Load a saved model
        
        Args:
            model_name: Name identifier
            version: Specific version (loads latest if None)
            
        Returns:
            Loaded sklearn model
        """
        if model_name not in self.registry:
            raise ValueError(f"Model '{model_name}' not found in registry")
        
        model_versions = self.registry[model_name]
        
        if version:
            # Load specific version
            model_info = next((m for m in model_versions if m['version'] == version), None)
            if not model_info:
                raise ValueError(f"Version '{version}' not found for model '{model_name}'")
        else:
            # Load latest version
            model_info = model_versions[-1]
        
        filepath = model_info['filepath']
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        # Verify integrity
        current_hash = self._calculate_file_hash(filepath)
        if current_hash != model_info['model_hash']:
            print(f"⚠️  Warning: Model file hash mismatch. File may be corrupted.")
        
        # Load model
        model = joblib.load(filepath)
        
        print(f"✅ Model loaded: {model_info['filename']}")
        print(f"   Version: {model_info['version']}")
        print(f"   Saved at: {model_info['saved_at']}")
        
        return model
    
    def list_models(self) -> Dict:
        """
        List all available models
        
        Returns:
            Dict with model names and their versions
        """
        return {
            name: [v['version'] for v in versions]
            for name, versions in self.registry.items()
        }
    
    def get_model_info(self, model_name: str, version: Optional[str] = None) -> Dict:
        """
        Get metadata for a specific model
        
        Args:
            model_name: Name identifier
            version: Specific version (latest if None)
            
        Returns:
            Model metadata dict
        """
        if model_name not in self.registry:
            raise ValueError(f"Model '{model_name}' not found")
        
        model_versions = self.registry[model_name]
        
        if version:
            model_info = next((m for m in model_versions if m['version'] == version), None)
        else:
            model_info = model_versions[-1]
        
        return model_info
    
    def delete_model(self, model_name: str, version: str):
        """
        Delete a specific model version
        
        Args:
            model_name: Name identifier
            version: Version to delete
        """
        if model_name not in self.registry:
            raise ValueError(f"Model '{model_name}' not found")
        
        model_versions = self.registry[model_name]
        model_info = next((m for m in model_versions if m['version'] == version), None)
        
        if not model_info:
            raise ValueError(f"Version '{version}' not found")
        
        # Delete file
        if os.path.exists(model_info['filepath']):
            os.remove(model_info['filepath'])
        
        # Remove from registry
        self.registry[model_name] = [m for m in model_versions if m['version'] != version]
        
        # Remove model entry if no versions left
        if not self.registry[model_name]:
            del self.registry[model_name]
        
        self.save_registry()
        
        print(f"✅ Model deleted: {model_info['filename']}")
    
    def _calculate_file_hash(self, filepath: str) -> str:
        """Calculate MD5 hash of file for integrity checking"""
        hash_md5 = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def cleanup_old_versions(self, model_name: str, keep_latest: int = 3):
        """
        Remove old versions, keeping only the latest N
        
        Args:
            model_name: Name identifier
            keep_latest: Number of latest versions to keep
        """
        if model_name not in self.registry:
            return
        
        model_versions = self.registry[model_name]
        
        if len(model_versions) <= keep_latest:
            return
        
        # Sort by saved_at
        sorted_versions = sorted(model_versions, key=lambda x: x['saved_at'], reverse=True)
        
        # Delete old versions
        for old_version in sorted_versions[keep_latest:]:
            try:
                self.delete_model(model_name, old_version['version'])
            except Exception as e:
                print(f"⚠️  Could not delete {old_version['filename']}: {e}")
        
        print(f"✅ Cleanup complete for '{model_name}'. Kept {keep_latest} latest versions.")
    
    def export_registry_report(self, filepath: str = 'models_report.txt'):
        """Generate human-readable report of all models"""
        report = "="*70 + "\n"
        report += "MODEL REGISTRY REPORT\n"
        report += "="*70 + "\n\n"
        
        for model_name, versions in self.registry.items():
            report += f"\n{'─'*70}\n"
            report += f"MODEL: {model_name}\n"
            report += f"{'─'*70}\n"
            report += f"Total Versions: {len(versions)}\n\n"
            
            for v in versions:
                report += f"  Version: {v['version']}\n"
                report += f"    Type: {v.get('model_type', 'Unknown')}\n"
                report += f"    Size: {v.get('file_size_mb', 0):.2f} MB\n"
                report += f"    Saved: {v.get('saved_at', 'Unknown')}\n"
                
                # Add performance metrics if available
                if 'accuracy' in v:
                    report += f"    Accuracy: {v['accuracy']:.4f}\n"
                if 'f1_score' in v:
                    report += f"    F1 Score: {v['f1_score']:.4f}\n"
                
                report += "\n"
        
        report += "="*70 + "\n"
        
        with open(filepath, 'w') as f:
            f.write(report)
        
        print(f"✅ Registry report saved: {filepath}")
        return report


# Convenience functions
def save_model(model: Any, name: str, metadata: Optional[Dict] = None) -> str:
    """
    Quick save function
    
    Args:
        model: Trained model
        name: Model name
        metadata: Optional metadata dict
        
    Returns:
        Path to saved file
    """
    manager = ModelManager()
    return manager.save_model(model, name, metadata)


def load_model(name: str, version: Optional[str] = None) -> Any:
    """
    Quick load function
    
    Args:
        name: Model name
        version: Specific version (latest if None)
        
    Returns:
        Loaded model
    """
    manager = ModelManager()
    return manager.load_model(name, version)


# Example usage
if __name__ == '__main__':
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split
    
    print("="*70)
    print("MODEL PERSISTENCE DEMO")
    print("="*70)
    
    # Create sample model
    X, y = make_classification(n_samples=1000, n_features=8, n_classes=3, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    accuracy = model.score(X_test, y_test)
    
    # Save model
    manager = ModelManager()
    manager.save_model(
        model=model,
        model_name='severity_classifier',
        metadata={
            'accuracy': accuracy,
            'n_estimators': 100,
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'description': 'Random Forest classifier for severity prediction'
        }
    )
    
    # List models
    print("\n📋 Available models:")
    print(json.dumps(manager.list_models(), indent=2))
    
    # Load model
    loaded_model = manager.load_model('severity_classifier')
    
    # Verify
    loaded_accuracy = loaded_model.score(X_test, y_test)
    print(f"\n✅ Verification: Accuracy matches = {abs(accuracy - loaded_accuracy) < 1e-10}")
    
    # Export report
    manager.export_registry_report()
