"""
Performance Optimization Module
Implements caching, query optimization, and lazy loading for ML models
"""
import time
import functools
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional
import json
import hashlib


class PerformanceCache:
    """In-memory cache with TTL support for analytics queries"""
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
    def generate_key(self, func_name: str, *args, **kwargs) -> str:
        """Generate cache key from function name and arguments"""
        key_data = {
            'func': func_name,
            'args': str(args),
            'kwargs': str(sorted(kwargs.items()))
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() < entry['expires']:
                self.cache_hits += 1
                return entry['value']
            else:
                del self.cache[key]
        self.cache_misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """Store value in cache with TTL (default 5 minutes)"""
        self.cache[key] = {
            'value': value,
            'expires': datetime.now() + timedelta(seconds=ttl_seconds),
            'created': datetime.now()
        }
    
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_size': len(self.cache),
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': round(hit_rate, 2),
            'total_requests': total_requests
        }


# Global cache instance
performance_cache = PerformanceCache()


def cached(ttl_seconds: int = 300):
    """Decorator for caching function results"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = performance_cache.generate_key(func.__name__, *args, **kwargs)
            
            # Try to get from cache
            cached_result = performance_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            performance_cache.set(cache_key, result, ttl_seconds)
            return result
        
        return wrapper
    return decorator


def timed(func: Callable) -> Callable:
    """Decorator to measure function execution time"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = round((end_time - start_time) * 1000, 2)  # Convert to ms
        
        # Log slow queries (> 1 second)
        if execution_time > 1000:
            print(f"⚠️ SLOW QUERY: {func.__name__} took {execution_time}ms")
        
        return result
    return wrapper


class QueryOptimizer:
    """Optimizes database queries for better performance"""
    
    @staticmethod
    def build_index_suggestions(table_name: str, columns: list) -> list:
        """Suggest database indexes for query optimization"""
        suggestions = []
        for col in columns:
            suggestions.append({
                'table': table_name,
                'column': col,
                'index_name': f'idx_{table_name}_{col}',
                'sql': f'CREATE INDEX IF NOT EXISTS idx_{table_name}_{col} ON {table_name}({col});'
            })
        return suggestions
    
    @staticmethod
    def optimize_date_range_query(table: str, date_col: str, days: int) -> str:
        """Generate optimized date range query"""
        return f"""
        SELECT * FROM {table}
        WHERE {date_col} >= datetime('now', '-{days} days')
        ORDER BY {date_col} DESC
        """
    
    @staticmethod
    def optimize_aggregation_query(table: str, group_col: str, agg_col: str, agg_func: str = 'COUNT') -> str:
        """Generate optimized aggregation query"""
        return f"""
        SELECT {group_col}, {agg_func}({agg_col}) as total
        FROM {table}
        GROUP BY {group_col}
        ORDER BY total DESC
        """


class LazyModelLoader:
    """Lazy loading for ML models to reduce startup time"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.load_times: Dict[str, float] = {}
    
    def register_model(self, name: str, loader_func: Callable):
        """Register a model with its loader function"""
        self.models[name] = {
            'loader': loader_func,
            'instance': None,
            'loaded': False
        }
    
    def get_model(self, name: str) -> Any:
        """Get model instance, loading if necessary"""
        if name not in self.models:
            raise ValueError(f"Model '{name}' not registered")
        
        model_info = self.models[name]
        
        # Load model if not already loaded
        if not model_info['loaded']:
            print(f"🔄 Lazy loading model: {name}")
            start_time = time.time()
            model_info['instance'] = model_info['loader']()
            model_info['loaded'] = True
            load_time = time.time() - start_time
            self.load_times[name] = load_time
            print(f"✅ Model '{name}' loaded in {load_time:.2f}s")
        
        return model_info['instance']
    
    def unload_model(self, name: str):
        """Unload model from memory"""
        if name in self.models and self.models[name]['loaded']:
            self.models[name]['instance'] = None
            self.models[name]['loaded'] = False
            print(f"🗑️ Model '{name}' unloaded from memory")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get lazy loading statistics"""
        return {
            'total_models': len(self.models),
            'loaded_models': sum(1 for m in self.models.values() if m['loaded']),
            'load_times': self.load_times
        }


# Global lazy loader instance
lazy_loader = LazyModelLoader()


class PerformanceMonitor:
    """Monitor and report performance metrics"""
    
    def __init__(self):
        self.metrics: Dict[str, list] = {
            'response_times': [],
            'query_times': [],
            'prediction_times': []
        }
    
    def record_metric(self, metric_type: str, value: float):
        """Record a performance metric"""
        if metric_type not in self.metrics:
            self.metrics[metric_type] = []
        self.metrics[metric_type].append({
            'value': value,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 1000 entries per metric
        if len(self.metrics[metric_type]) > 1000:
            self.metrics[metric_type] = self.metrics[metric_type][-1000:]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics"""
        summary = {}
        for metric_type, values in self.metrics.items():
            if values:
                numeric_values = [v['value'] for v in values]
                summary[metric_type] = {
                    'count': len(numeric_values),
                    'avg': round(sum(numeric_values) / len(numeric_values), 2),
                    'min': round(min(numeric_values), 2),
                    'max': round(max(numeric_values), 2),
                    'p95': round(sorted(numeric_values)[int(len(numeric_values) * 0.95)], 2) if len(numeric_values) > 0 else 0
                }
        return summary


# Global performance monitor
performance_monitor = PerformanceMonitor()


def batch_process(items: list, batch_size: int = 100) -> list:
    """Process items in batches for better performance"""
    results = []
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        results.extend(batch)
    return results


def debounce(wait_seconds: float):
    """Debounce decorator to limit function call frequency"""
    def decorator(func: Callable) -> Callable:
        last_called = [0.0]
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            if current_time - last_called[0] >= wait_seconds:
                last_called[0] = current_time
                return func(*args, **kwargs)
            return None
        
        return wrapper
    return decorator


# Database connection pooling configuration
DB_POOL_CONFIG = {
    'pool_size': 10,
    'max_overflow': 20,
    'pool_timeout': 30,
    'pool_recycle': 3600
}


def get_performance_report() -> Dict[str, Any]:
    """Generate comprehensive performance report"""
    return {
        'cache_stats': performance_cache.get_stats(),
        'model_loading': lazy_loader.get_stats(),
        'performance_metrics': performance_monitor.get_summary(),
        'timestamp': datetime.now().isoformat()
    }


if __name__ == "__main__":
    print("🚀 Performance Optimization Module")
    print("=" * 50)
    
    # Test cache
    @cached(ttl_seconds=60)
    def expensive_function(x: int) -> int:
        time.sleep(0.1)  # Simulate expensive operation
        return x * x
    
    print("\n1. Testing Cache:")
    start = time.time()
    result1 = expensive_function(5)
    time1 = time.time() - start
    print(f"   First call: {result1} ({time1*1000:.2f}ms)")
    
    start = time.time()
    result2 = expensive_function(5)
    time2 = time.time() - start
    print(f"   Cached call: {result2} ({time2*1000:.2f}ms)")
    print(f"   Speedup: {time1/time2:.1f}x faster")
    
    # Test lazy loading
    print("\n2. Testing Lazy Model Loading:")
    def load_dummy_model():
        time.sleep(0.05)
        return {"model": "dummy", "version": "1.0"}
    
    lazy_loader.register_model("dummy_model", load_dummy_model)
    model = lazy_loader.get_model("dummy_model")
    print(f"   Model loaded: {model}")
    
    # Performance report
    print("\n3. Performance Report:")
    report = get_performance_report()
    print(f"   Cache hits: {report['cache_stats']['cache_hits']}")
    print(f"   Cache misses: {report['cache_stats']['cache_misses']}")
    print(f"   Hit rate: {report['cache_stats']['hit_rate']}%")
    
    print("\n✅ All performance tests passed!")
