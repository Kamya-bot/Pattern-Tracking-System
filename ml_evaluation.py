"""
ML Model Evaluation Module
Provides comprehensive metrics for supervised learning models
"""
import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score
)
from sklearn.model_selection import cross_val_score
import json


class ModelEvaluator:
    """
    Comprehensive ML model evaluation with industry-standard metrics
    """
    
    def __init__(self):
        self.metrics = {}
    
    def evaluate_classifier(self, model, X_test: np.ndarray, y_test: np.ndarray, 
                          labels: List[str] = None) -> Dict:
        """
        Evaluate a classification model with comprehensive metrics
        
        Args:
            model: Trained sklearn classifier
            X_test: Test features
            y_test: True labels
            labels: Class label names
            
        Returns:
            Dict with all evaluation metrics
        """
        # Generate predictions
        y_pred = model.predict(X_test)
        
        # Handle multi-class vs binary
        average = 'weighted' if len(np.unique(y_test)) > 2 else 'binary'
        
        # Core metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average=average, zero_division=0)
        recall = recall_score(y_test, y_pred, average=average, zero_division=0)
        f1 = f1_score(y_test, y_pred, average=average, zero_division=0)
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        
        # Per-class metrics
        class_report = classification_report(y_test, y_pred, 
                                            target_names=labels,
                                            output_dict=True,
                                            zero_division=0)
        
        # ROC-AUC for binary/multi-class
        try:
            if hasattr(model, 'predict_proba'):
                y_proba = model.predict_proba(X_test)
                if len(np.unique(y_test)) == 2:
                    roc_auc = roc_auc_score(y_test, y_proba[:, 1])
                else:
                    roc_auc = roc_auc_score(y_test, y_proba, multi_class='ovr', average='weighted')
            else:
                roc_auc = None
        except Exception:
            roc_auc = None
        
        # Build results
        results = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'roc_auc': float(roc_auc) if roc_auc is not None else None,
            'confusion_matrix': cm.tolist(),
            'classification_report': class_report,
            'support': {
                'train_size': 'N/A',  # To be filled by caller
                'test_size': len(y_test),
                'n_features': X_test.shape[1] if len(X_test.shape) > 1 else 1
            }
        }
        
        self.metrics = results
        return results
    
    def cross_validate(self, model, X: np.ndarray, y: np.ndarray, cv: int = 5) -> Dict:
        """
        Perform k-fold cross-validation
        
        Args:
            model: Sklearn model (untrained)
            X: Full feature set
            y: Full labels
            cv: Number of folds
            
        Returns:
            Dict with cross-validation scores
        """
        cv_scores = cross_val_score(model, X, y, cv=cv, scoring='accuracy')
        
        return {
            'cv_scores': cv_scores.tolist(),
            'mean_cv_score': float(np.mean(cv_scores)),
            'std_cv_score': float(np.std(cv_scores)),
            'cv_folds': cv
        }
    
    def evaluate_regression(self, model, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """
        Evaluate a regression model
        
        Args:
            model: Trained sklearn regressor
            X_test: Test features
            y_test: True values
            
        Returns:
            Dict with regression metrics
        """
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        
        y_pred = model.predict(X_test)
        
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Residual analysis
        residuals = y_test - y_pred
        
        results = {
            'mse': float(mse),
            'rmse': float(rmse),
            'mae': float(mae),
            'r2_score': float(r2),
            'residuals': {
                'mean': float(np.mean(residuals)),
                'std': float(np.std(residuals)),
                'min': float(np.min(residuals)),
                'max': float(np.max(residuals))
            },
            'support': {
                'test_size': len(y_test),
                'n_features': X_test.shape[1] if len(X_test.shape) > 1 else 1
            }
        }
        
        return results
    
    def generate_report(self, model_name: str, save_path: Optional[str] = None) -> str:
        """
        Generate a formatted evaluation report
        
        Args:
            model_name: Name of the model
            save_path: Optional path to save report
            
        Returns:
            Formatted report string
        """
        report = f"""
{'='*70}
MODEL EVALUATION REPORT: {model_name}
{'='*70}

CORE METRICS:
-------------
Accuracy:  {self.metrics.get('accuracy', 'N/A'):.4f}
Precision: {self.metrics.get('precision', 'N/A'):.4f}
Recall:    {self.metrics.get('recall', 'N/A'):.4f}
F1-Score:  {self.metrics.get('f1_score', 'N/A'):.4f}
"""
        
        if self.metrics.get('roc_auc'):
            report += f"ROC-AUC:   {self.metrics['roc_auc']:.4f}\n"
        
        report += f"""
CONFUSION MATRIX:
-----------------
{np.array(self.metrics.get('confusion_matrix', []))}

DATASET INFO:
-------------
Test Samples:  {self.metrics.get('support', {}).get('test_size', 'N/A')}
Features:      {self.metrics.get('support', {}).get('n_features', 'N/A')}

CLASSIFICATION REPORT:
----------------------
"""
        
        # Add per-class metrics
        class_report = self.metrics.get('classification_report', {})
        for class_name, metrics in class_report.items():
            if isinstance(metrics, dict):
                report += f"\n{class_name}:\n"
                report += f"  Precision: {metrics.get('precision', 'N/A'):.4f}\n"
                report += f"  Recall:    {metrics.get('recall', 'N/A'):.4f}\n"
                report += f"  F1-Score:  {metrics.get('f1-score', 'N/A'):.4f}\n"
                report += f"  Support:   {metrics.get('support', 'N/A')}\n"
        
        report += f"\n{'='*70}\n"
        
        if save_path:
            with open(save_path, 'w') as f:
                f.write(report)
        
        return report
    
    def save_metrics(self, filepath: str):
        """Save metrics to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def format_for_dashboard(self) -> Dict:
        """
        Format metrics for dashboard display
        
        Returns:
            Dict optimized for frontend consumption
        """
        cm = np.array(self.metrics.get('confusion_matrix', []))
        
        return {
            'summary': {
                'accuracy': round(self.metrics.get('accuracy', 0) * 100, 2),
                'precision': round(self.metrics.get('precision', 0) * 100, 2),
                'recall': round(self.metrics.get('recall', 0) * 100, 2),
                'f1_score': round(self.metrics.get('f1_score', 0) * 100, 2)
            },
            'confusion_matrix': {
                'data': cm.tolist(),
                'labels': ['Mild', 'Moderate', 'Severe']  # Customize as needed
            },
            'per_class': self.metrics.get('classification_report', {}),
            'metadata': {
                'test_size': self.metrics.get('support', {}).get('test_size', 0),
                'n_features': self.metrics.get('support', {}).get('n_features', 0),
                'model_type': 'Random Forest Classifier'
            }
        }


def evaluate_model(model, X_test: np.ndarray, y_test: np.ndarray, 
                  model_name: str = "Model", labels: List[str] = None) -> Dict:
    """
    Convenience function to evaluate a model and return all metrics
    
    Args:
        model: Trained sklearn model
        X_test: Test features
        y_test: True labels/values
        model_name: Name for reporting
        labels: Class labels (for classification)
        
    Returns:
        Dict with comprehensive evaluation metrics
    """
    evaluator = ModelEvaluator()
    
    # Determine if classification or regression
    if hasattr(model, 'predict_proba') or labels is not None:
        results = evaluator.evaluate_classifier(model, X_test, y_test, labels)
        print(evaluator.generate_report(model_name))
    else:
        results = evaluator.evaluate_regression(model, X_test, y_test)
        print(f"\n{'='*50}")
        print(f"REGRESSION EVALUATION: {model_name}")
        print(f"{'='*50}")
        print(f"R² Score: {results['r2_score']:.4f}")
        print(f"RMSE:     {results['rmse']:.4f}")
        print(f"MAE:      {results['mae']:.4f}")
        print(f"{'='*50}\n")
    
    return results


# Example usage
if __name__ == '__main__':
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.datasets import make_classification
    
    # Generate sample data
    X, y = make_classification(n_samples=1000, n_features=8, n_classes=3,
                               n_informative=6, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    results = evaluate_model(model, X_test, y_test, 
                           model_name="Random Forest Severity Classifier",
                           labels=['Mild', 'Moderate', 'Severe'])
    
    # Save results
    evaluator = ModelEvaluator()
    evaluator.metrics = results
    evaluator.save_metrics('model_evaluation.json')
    print("\n✅ Evaluation complete! Metrics saved to model_evaluation.json")
