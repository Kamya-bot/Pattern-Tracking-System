"""
Security Enhancement Module
Implements input validation, rate limiting, and error handling
"""
import re
import time
import functools
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime, timedelta
import hashlib
import secrets


class InputValidator:
    """Validates and sanitizes user input"""
    
    # Validation patterns
    PATTERNS = {
        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'phone': r'^\+?[1-9]\d{1,14}$',
        'alphanumeric': r'^[a-zA-Z0-9]+$',
        'alpha': r'^[a-zA-Z]+$',
        'numeric': r'^[0-9]+$',
        'uuid': r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    }
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        if not email or not isinstance(email, str):
            return False
        return bool(re.match(InputValidator.PATTERNS['email'], email.strip()))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        if not phone or not isinstance(phone, str):
            return False
        return bool(re.match(InputValidator.PATTERNS['phone'], phone.strip()))
    
    @staticmethod
    def validate_length(text: str, min_len: int = 1, max_len: int = 1000) -> bool:
        """Validate text length"""
        if not isinstance(text, str):
            return False
        return min_len <= len(text.strip()) <= max_len
    
    @staticmethod
    def validate_choice(value: Any, choices: List[Any]) -> bool:
        """Validate value is in allowed choices"""
        return value in choices
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not isinstance(text, str):
            return ""
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Strip whitespace
        text = text.strip()
        
        # Limit length
        if len(text) > max_length:
            text = text[:max_length]
        
        # Remove potentially dangerous HTML/JS
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe',
            r'<object',
            r'<embed'
        ]
        
        for pattern in dangerous_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
        
        return text
    
    @staticmethod
    def validate_severity(severity: int) -> bool:
        """Validate severity score (1-10)"""
        return isinstance(severity, int) and 1 <= severity <= 10
    
    @staticmethod
    def validate_date(date_str: str) -> bool:
        """Validate date format (YYYY-MM-DD)"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_json_structure(data: dict, required_fields: List[str]) -> tuple:
        """Validate JSON has required fields"""
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        return True, "Valid"
    
    @staticmethod
    def validate_report_data(data: dict) -> tuple:
        """Validate health report submission data"""
        required_fields = ['symptoms', 'severity', 'location']
        is_valid, message = InputValidator.validate_json_structure(data, required_fields)
        
        if not is_valid:
            return False, message
        
        # Validate symptoms
        symptoms = data.get('symptoms', [])
        if not isinstance(symptoms, list) or len(symptoms) == 0:
            return False, "Symptoms must be a non-empty list"
        
        if len(symptoms) > 20:
            return False, "Too many symptoms (max 20)"
        
        # Validate severity
        severity = data.get('severity')
        if not InputValidator.validate_severity(severity):
            return False, "Severity must be an integer between 1 and 10"
        
        # Validate location
        location = data.get('location', '')
        if not InputValidator.validate_length(location, 1, 200):
            return False, "Location must be between 1 and 200 characters"
        
        return True, "Valid report data"


class RateLimiter:
    """Rate limiting to prevent abuse"""
    
    def __init__(self):
        self.requests: Dict[str, List[float]] = {}
        self.blocked_ips: Dict[str, float] = {}
    
    def is_blocked(self, identifier: str) -> bool:
        """Check if identifier is currently blocked"""
        if identifier in self.blocked_ips:
            if time.time() < self.blocked_ips[identifier]:
                return True
            else:
                del self.blocked_ips[identifier]
        return False
    
    def block_identifier(self, identifier: str, duration_seconds: int = 300):
        """Block identifier for specified duration"""
        self.blocked_ips[identifier] = time.time() + duration_seconds
    
    def check_rate_limit(
        self,
        identifier: str,
        max_requests: int = 100,
        window_seconds: int = 60
    ) -> tuple:
        """Check if identifier exceeds rate limit"""
        
        # Check if blocked
        if self.is_blocked(identifier):
            return False, "Rate limit exceeded. Please try again later."
        
        current_time = time.time()
        window_start = current_time - window_seconds
        
        # Initialize or clean old requests
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Remove old requests outside the window
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > window_start
        ]
        
        # Check rate limit
        if len(self.requests[identifier]) >= max_requests:
            self.block_identifier(identifier, duration_seconds=300)  # Block for 5 minutes
            return False, f"Rate limit exceeded: {max_requests} requests per {window_seconds} seconds"
        
        # Record this request
        self.requests[identifier].append(current_time)
        
        remaining = max_requests - len(self.requests[identifier])
        return True, f"{remaining} requests remaining"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics"""
        return {
            'total_identifiers': len(self.requests),
            'blocked_identifiers': len(self.blocked_ips),
            'active_requests': sum(len(reqs) for reqs in self.requests.values())
        }


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(max_requests: int = 100, window_seconds: int = 60):
    """Decorator for rate limiting endpoints"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Try to extract identifier (IP address or user ID)
            # In a real application, this would come from request context
            identifier = kwargs.get('ip_address', 'unknown')
            
            is_allowed, message = rate_limiter.check_rate_limit(
                identifier, max_requests, window_seconds
            )
            
            if not is_allowed:
                return {'error': message, 'status': 429}, 429
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


class SecurityHeaders:
    """Security headers for HTTP responses"""
    
    @staticmethod
    def get_headers() -> Dict[str, str]:
        """Get recommended security headers"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdn.tailwindcss.com https://cdn.plot.ly; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:;",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
        }


class ErrorHandler:
    """Secure error handling"""
    
    @staticmethod
    def safe_error_response(error: Exception, include_details: bool = False) -> Dict[str, Any]:
        """Generate safe error response"""
        error_id = secrets.token_hex(8)
        
        response = {
            'error': 'An error occurred',
            'error_id': error_id,
            'timestamp': datetime.now().isoformat()
        }
        
        # In development, include more details
        if include_details:
            response['error_type'] = type(error).__name__
            response['error_message'] = str(error)
        
        # Log full error server-side (would integrate with logger.py)
        print(f"❌ Error {error_id}: {type(error).__name__}: {str(error)}")
        
        return response
    
    @staticmethod
    def validate_and_handle(validator_func: Callable, data: Any) -> tuple:
        """Validate data and return standardized response"""
        try:
            is_valid, message = validator_func(data)
            if is_valid:
                return True, None
            else:
                return False, {'error': message, 'status': 400}
        except Exception as e:
            return False, ErrorHandler.safe_error_response(e)


class TokenManager:
    """Manage security tokens and sessions"""
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate secure random token"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password (simple implementation - use bcrypt in production)"""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${pwd_hash.hex()}"
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            salt, pwd_hash = hashed.split('$')
            new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return new_hash.hex() == pwd_hash
        except Exception:
            return False


class SQLInjectionProtector:
    """Protect against SQL injection attacks"""
    
    DANGEROUS_PATTERNS = [
        r'(\bUNION\b.*\bSELECT\b)',
        r'(\bDROP\b.*\bTABLE\b)',
        r'(\bINSERT\b.*\bINTO\b)',
        r'(\bDELETE\b.*\bFROM\b)',
        r'(\bUPDATE\b.*\bSET\b)',
        r'(--|#|/\*|\*/)',
        r'(\bEXEC\b|\bEXECUTE\b)',
        r'(\bxp_\w+)',
        r'(;.*\bDROP\b)',
    ]
    
    @staticmethod
    def is_safe_input(user_input: str) -> bool:
        """Check if input contains SQL injection attempts"""
        if not isinstance(user_input, str):
            return True
        
        for pattern in SQLInjectionProtector.DANGEROUS_PATTERNS:
            if re.search(pattern, user_input, re.IGNORECASE):
                print(f"⚠️ Potential SQL injection detected: {pattern}")
                return False
        
        return True


def get_security_config() -> Dict[str, Any]:
    """Get security configuration"""
    return {
        'rate_limiting': {
            'enabled': True,
            'default_max_requests': 100,
            'default_window_seconds': 60,
            'block_duration_seconds': 300
        },
        'input_validation': {
            'enabled': True,
            'max_string_length': 1000,
            'max_array_size': 20
        },
        'security_headers': {
            'enabled': True,
            'headers': SecurityHeaders.get_headers()
        },
        'error_handling': {
            'include_details': False,  # Set to True in development
            'log_errors': True
        }
    }


if __name__ == "__main__":
    print("🔒 Security Enhancement Module Tests")
    print("=" * 50)
    
    # Test input validation
    print("\n1. Testing Input Validation:")
    validator = InputValidator()
    
    test_cases = [
        ('email', 'user@example.com', True),
        ('email', 'invalid-email', False),
        ('severity', 5, True),
        ('severity', 15, False),
    ]
    
    for test_type, value, expected in test_cases:
        if test_type == 'email':
            result = validator.validate_email(value)
        elif test_type == 'severity':
            result = validator.validate_severity(value)
        
        status = "✅" if result == expected else "❌"
        print(f"   {status} {test_type}({value}): {result}")
    
    # Test rate limiting
    print("\n2. Testing Rate Limiting:")
    limiter = RateLimiter()
    
    for i in range(5):
        allowed, msg = limiter.check_rate_limit('test_user', max_requests=3, window_seconds=60)
        status = "✅" if allowed else "❌"
        print(f"   {status} Request {i+1}: {msg}")
    
    # Test sanitization
    print("\n3. Testing Input Sanitization:")
    dangerous_input = "<script>alert('XSS')</script>Hello"
    sanitized = validator.sanitize_string(dangerous_input)
    print(f"   Original: {dangerous_input}")
    print(f"   Sanitized: {sanitized}")
    
    # Test SQL injection detection
    print("\n4. Testing SQL Injection Protection:")
    test_inputs = [
        "normal input",
        "'; DROP TABLE users; --",
        "SELECT * FROM users WHERE id=1"
    ]
    
    for test_input in test_inputs:
        is_safe = SQLInjectionProtector.is_safe_input(test_input)
        status = "✅" if is_safe else "⚠️"
        print(f"   {status} '{test_input[:30]}...': {'Safe' if is_safe else 'BLOCKED'}")
    
    print("\n✅ All security tests completed!")
