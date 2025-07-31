"""
Security patches and utilities for NutriBot
"""
import os
import hashlib
import mimetypes
from pathlib import Path
import re
import html
from typing import Dict, Any, Optional
import time
from functools import wraps

class SecurityValidator:
    """Security validation utilities"""
    
    # Safe file extensions
    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    ALLOWED_MODEL_EXTENSIONS = {'.pkl', '.joblib'}
    
    # Maximum file sizes (bytes)
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_MODEL_SIZE = 100 * 1024 * 1024  # 100MB
    
    # Regex timeout (seconds)
    REGEX_TIMEOUT = 5
    
    @staticmethod
    def validate_file_upload(uploaded_file) -> Dict[str, Any]:
        """
        Comprehensive file upload validation
        
        Returns:
            Dict with validation results
        """
        if not uploaded_file:
            return {'valid': False, 'error': 'No file provided'}
        
        # Check file size
        if hasattr(uploaded_file, 'size') and uploaded_file.size > SecurityValidator.MAX_IMAGE_SIZE:
            return {'valid': False, 'error': f'File too large: {uploaded_file.size} bytes'}
        
        # Check file extension
        file_ext = Path(uploaded_file.name).suffix.lower()
        if file_ext not in SecurityValidator.ALLOWED_IMAGE_EXTENSIONS:
            return {'valid': False, 'error': f'Invalid file type: {file_ext}'}
        
        # Check MIME type
        mime_type, _ = mimetypes.guess_type(uploaded_file.name)
        if not mime_type or not mime_type.startswith('image/'):
            return {'valid': False, 'error': f'Invalid MIME type: {mime_type}'}
        
        # Check for malicious content (basic)
        try:
            content = uploaded_file.read(1024)  # Read first 1KB
            uploaded_file.seek(0)  # Reset file pointer
            
            # Check for suspicious patterns
            suspicious_patterns = [b'<script', b'javascript:', b'<?php', b'<%']
            for pattern in suspicious_patterns:
                if pattern in content.lower():
                    return {'valid': False, 'error': 'Suspicious content detected'}
        except Exception as e:
            return {'valid': False, 'error': f'File read error: {str(e)}'}
        
        return {'valid': True, 'error': None}
    
    @staticmethod
    def sanitize_text_input(text: str, max_length: int = 1000) -> str:
        """
        Sanitize text input to prevent XSS and injection attacks
        """
        if not isinstance(text, str):
            return ""
        
        # Limit length
        text = text[:max_length]
        
        # HTML escape
        text = html.escape(text)
        
        # Remove potentially dangerous characters
        text = re.sub(r'[<>"\']', '', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @staticmethod
    def validate_nutrition_input(nutrition_data: Dict[str, float]) -> Dict[str, Any]:
        """
        Validate nutrition input values
        """
        if not isinstance(nutrition_data, dict):
            return {'valid': False, 'error': 'Invalid nutrition data format'}
        
        # Define reasonable ranges for nutrition values (per 100g)
        valid_ranges = {
            'Calories': (0, 900),
            'Protein': (0, 100),
            'TotalFat': (0, 100),
            'Carbohydrate': (0, 100),
            'Sugar': (0, 100),
            'Sodium': (0, 10),  # grams
            'SaturatedFat': (0, 100),
            'Calcium': (0, 5),
            'Iron': (0, 100),
            'Potassium': (0, 10),
            'VitaminC': (0, 1000),
            'VitaminE': (0, 100),
            'VitaminD': (0, 100)
        }
        
        for key, value in nutrition_data.items():
            if not isinstance(value, (int, float)):
                return {'valid': False, 'error': f'Invalid value type for {key}'}
            
            if key in valid_ranges:
                min_val, max_val = valid_ranges[key]
                if not (min_val <= value <= max_val):
                    return {'valid': False, 'error': f'{key} value {value} out of range [{min_val}, {max_val}]'}
        
        return {'valid': True, 'error': None}
    
    @staticmethod
    def safe_regex_search(pattern: str, text: str, timeout: int = 5) -> Optional[re.Match]:
        """
        Perform regex search with timeout to prevent ReDoS
        """
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Regex timeout")
        
        # Set timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        
        try:
            result = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            signal.alarm(0)  # Cancel timeout
            return result
        except TimeoutError:
            signal.alarm(0)
            return None
        except Exception:
            signal.alarm(0)
            return None
    
    @staticmethod
    def validate_model_path(model_path: str, base_dir: str = 'models') -> str:
        """
        Validate and sanitize model file paths to prevent path traversal
        """
        # Resolve absolute paths
        base_path = Path(base_dir).resolve()
        requested_path = Path(model_path).resolve()
        
        # Check if requested path is within base directory
        try:
            requested_path.relative_to(base_path)
        except ValueError:
            raise ValueError(f"Path traversal attempt detected: {model_path}")
        
        # Check file extension
        if requested_path.suffix not in SecurityValidator.ALLOWED_MODEL_EXTENSIONS:
            raise ValueError(f"Invalid model file extension: {requested_path.suffix}")
        
        return str(requested_path)
    
    @staticmethod
    def verify_model_integrity(model_path: str, expected_hash: Optional[str] = None) -> bool:
        """
        Verify model file integrity using hash
        """
        if not os.path.exists(model_path):
            return False
        
        if expected_hash:
            with open(model_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            return file_hash == expected_hash
        
        return True

class RateLimiter:
    """Simple rate limiter for API endpoints"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed for client"""
        now = time.time()
        
        # Clean old entries
        self.requests = {
            cid: times for cid, times in self.requests.items()
            if any(t > now - self.window_seconds for t in times)
        }
        
        # Get client's recent requests
        client_requests = self.requests.get(client_id, [])
        recent_requests = [t for t in client_requests if t > now - self.window_seconds]
        
        if len(recent_requests) >= self.max_requests:
            return False
        
        # Add current request
        recent_requests.append(now)
        self.requests[client_id] = recent_requests
        
        return True

def rate_limit(max_requests: int = 100, window_seconds: int = 3600):
    """Rate limiting decorator"""
    limiter = RateLimiter(max_requests, window_seconds)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use session state as client ID for Streamlit
            import streamlit as st
            client_id = st.session_state.get('session_id', 'anonymous')
            
            if not limiter.is_allowed(client_id):
                st.error("Rate limit exceeded. Please try again later.")
                return None
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Example usage functions
def secure_file_upload():
    """Secure file upload with validation"""
    import streamlit as st
    
    uploaded_file = st.file_uploader(
        "Choose an image...",
        type=["jpg", "jpeg", "png"]
    )
    
    if uploaded_file:
        validation = SecurityValidator.validate_file_upload(uploaded_file)
        if not validation['valid']:
            st.error(f"File validation failed: {validation['error']}")
            return None
        return uploaded_file
    
    return None

def secure_text_input(label: str, max_length: int = 1000):
    """Secure text input with sanitization"""
    import streamlit as st
    
    raw_input = st.text_input(label)
    return SecurityValidator.sanitize_text_input(raw_input, max_length)

def secure_model_loading(model_path: str, expected_hash: Optional[str] = None):
    """Secure model loading with validation"""
    import joblib
    
    try:
        # Validate path
        safe_path = SecurityValidator.validate_model_path(model_path)
        
        # Verify integrity
        if not SecurityValidator.verify_model_integrity(safe_path, expected_hash):
            raise ValueError("Model integrity check failed")
        
        # Load model
        return joblib.load(safe_path)
    
    except Exception as e:
        raise ValueError(f"Secure model loading failed: {str(e)}")