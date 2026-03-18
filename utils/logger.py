"""
Production Logging System
Provides structured logging for API requests, ML predictions, and errors
"""
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
import json
from functools import wraps
from flask import request, g
import time


class StructuredLogger:
    """
    Enhanced logging with structured output and multiple handlers
    """
    
    def __init__(self, name: str = 'health_tracking', log_dir: str = 'logs'):
        self.name = name
        self.log_dir = log_dir
        self.ensure_log_directory()
        self.logger = self._setup_logger()
    
    def ensure_log_directory(self):
        """Create logs directory if it doesn't exist"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            print(f"✅ Created logs directory: {self.log_dir}")
    
    def _setup_logger(self) -> logging.Logger:
        """
        Configure logger with multiple handlers
        
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers to avoid duplicates
        logger.handlers.clear()
        
        # Format for log messages
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # JSON formatter for structured logs
        json_formatter = logging.Formatter(
            '%(message)s'
        )
        
        # 1. Console Handler (INFO and above)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 2. File Handler - General Log (Rotating)
        general_file = os.path.join(self.log_dir, 'application.log')
        file_handler = RotatingFileHandler(
            general_file,
            maxBytes=10*1024*1024,  # 10 MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # 3. Error File Handler (ERROR and above)
        error_file = os.path.join(self.log_dir, 'errors.log')
        error_handler = RotatingFileHandler(
            error_file,
            maxBytes=10*1024*1024,
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
        
        # 4. ML Predictions Log (JSON format)
        ml_file = os.path.join(self.log_dir, 'ml_predictions.log')
        ml_handler = RotatingFileHandler(
            ml_file,
            maxBytes=10*1024*1024,
            backupCount=5
        )
        ml_handler.setLevel(logging.INFO)
        ml_handler.setFormatter(json_formatter)
        ml_handler.addFilter(lambda record: 'ML_PREDICTION' in record.msg)
        logger.addHandler(ml_handler)
        
        # 5. API Requests Log
        api_file = os.path.join(self.log_dir, 'api_requests.log')
        api_handler = RotatingFileHandler(
            api_file,
            maxBytes=10*1024*1024,
            backupCount=5
        )
        api_handler.setLevel(logging.INFO)
        api_handler.setFormatter(json_formatter)
        api_handler.addFilter(lambda record: 'API_REQUEST' in record.msg)
        logger.addHandler(api_handler)
        
        return logger
    
    def log_api_request(self, endpoint: str, method: str, status_code: int,
                       duration_ms: float, ip_address: str = None):
        """
        Log API request with structured data
        
        Args:
            endpoint: API endpoint path
            method: HTTP method (GET, POST, etc.)
            status_code: HTTP response code
            duration_ms: Request duration in milliseconds
            ip_address: Client IP address
        """
        log_data = {
            'type': 'API_REQUEST',
            'timestamp': datetime.now().isoformat(),
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'duration_ms': round(duration_ms, 2),
            'ip_address': ip_address
        }
        
        self.logger.info(json.dumps(log_data))
    
    def log_ml_prediction(self, model_name: str, input_data: dict,
                         prediction: any, confidence: float = None):
        """
        Log ML model prediction
        
        Args:
            model_name: Name of ML model
            input_data: Input features
            prediction: Model prediction
            confidence: Prediction confidence (if available)
        """
        log_data = {
            'type': 'ML_PREDICTION',
            'timestamp': datetime.now().isoformat(),
            'model': model_name,
            'input': input_data,
            'prediction': str(prediction),
            'confidence': confidence
        }
        
        self.logger.info(json.dumps(log_data))
    
    def log_anomaly_detection(self, anomaly_date: str, severity: str,
                             score: float, explanation: str):
        """
        Log detected anomaly
        
        Args:
            anomaly_date: Date of anomaly
            severity: Severity level
            score: Anomaly score
            explanation: Human-readable explanation
        """
        log_data = {
            'type': 'ANOMALY_DETECTED',
            'timestamp': datetime.now().isoformat(),
            'anomaly_date': anomaly_date,
            'severity': severity,
            'score': score,
            'explanation': explanation
        }
        
        self.logger.warning(json.dumps(log_data))
    
    def log_error(self, error_type: str, error_message: str,
                 stack_trace: str = None, context: dict = None):
        """
        Log error with context
        
        Args:
            error_type: Type of error
            error_message: Error message
            stack_trace: Full stack trace
            context: Additional context
        """
        log_data = {
            'type': 'ERROR',
            'timestamp': datetime.now().isoformat(),
            'error_type': error_type,
            'message': error_message,
            'stack_trace': stack_trace,
            'context': context or {}
        }
        
        self.logger.error(json.dumps(log_data))
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)


# Global logger instance
_logger = None

def get_logger(name: str = 'health_tracking') -> StructuredLogger:
    """
    Get or create logger instance (Singleton pattern)
    
    Args:
        name: Logger name
        
    Returns:
        StructuredLogger instance
    """
    global _logger
    if _logger is None:
        _logger = StructuredLogger(name)
    return _logger


# Flask Decorators

def log_api_call(f):
    """
    Decorator to automatically log API calls
    
    Usage:
        @app.route('/api/endpoint')
        @log_api_call
        def endpoint():
            return {"data": "value"}
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger = get_logger()
        
        # Record start time
        g.start_time = time.time()
        
        # Get request info
        endpoint = request.path
        method = request.method
        ip_address = request.remote_addr
        
        try:
            # Execute the route function
            response = f(*args, **kwargs)
            
            # Calculate duration
            duration_ms = (time.time() - g.start_time) * 1000
            
            # Determine status code
            if isinstance(response, tuple):
                status_code = response[1]
            else:
                status_code = 200
            
            # Log the request
            logger.log_api_request(
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                duration_ms=duration_ms,
                ip_address=ip_address
            )
            
            return response
            
        except Exception as e:
            # Log error
            duration_ms = (time.time() - g.start_time) * 1000
            
            logger.log_error(
                error_type=type(e).__name__,
                error_message=str(e),
                context={
                    'endpoint': endpoint,
                    'method': method,
                    'ip_address': ip_address,
                    'duration_ms': duration_ms
                }
            )
            
            # Re-raise the exception
            raise
    
    return decorated_function


def log_ml_inference(model_name: str):
    """
    Decorator to log ML model predictions
    
    Usage:
        @log_ml_inference('severity_classifier')
        def predict_severity(symptoms):
            return model.predict(symptoms)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            logger = get_logger()
            
            try:
                # Execute prediction
                result = f(*args, **kwargs)
                
                # Extract input and output
                input_data = str(args) if args else str(kwargs)
                
                # Log prediction
                if isinstance(result, tuple) and len(result) == 2:
                    prediction, confidence = result
                    logger.log_ml_prediction(
                        model_name=model_name,
                        input_data=input_data,
                        prediction=prediction,
                        confidence=confidence
                    )
                else:
                    logger.log_ml_prediction(
                        model_name=model_name,
                        input_data=input_data,
                        prediction=result
                    )
                
                return result
                
            except Exception as e:
                logger.log_error(
                    error_type='ML_INFERENCE_ERROR',
                    error_message=str(e),
                    context={
                        'model': model_name,
                        'input': str(args) or str(kwargs)
                    }
                )
                raise
        
        return decorated_function
    return decorator


# Example Usage
if __name__ == '__main__':
    # Initialize logger
    logger = get_logger()
    
    print("="*70)
    print("LOGGING SYSTEM DEMO")
    print("="*70)
    
    # Test different log levels
    logger.debug("This is a debug message")
    logger.info("✅ Logging system initialized")
    logger.warning("⚠️  This is a warning")
    logger.error("❌ This is an error")
    
    # Test structured logging
    logger.log_api_request(
        endpoint='/api/admin/analytics',
        method='GET',
        status_code=200,
        duration_ms=45.23,
        ip_address='192.168.1.100'
    )
    
    logger.log_ml_prediction(
        model_name='severity_classifier',
        input_data={'fever': 1, 'cough': 1},
        prediction='Moderate',
        confidence=0.85
    )
    
    logger.log_anomaly_detection(
        anomaly_date='2024-03-08',
        severity='high',
        score=0.92,
        explanation='Report count 3x higher than normal'
    )
    
    logger.log_error(
        error_type='DatabaseError',
        error_message='Connection timeout',
        context={'database': 'pattern_tracking.db', 'timeout': 30}
    )
    
    print("\n✅ Logs written to:")
    print(f"   • logs/application.log (all levels)")
    print(f"   • logs/errors.log (errors only)")
    print(f"   • logs/ml_predictions.log (ML predictions)")
    print(f"   • logs/api_requests.log (API requests)")
    print("\n" + "="*70)
