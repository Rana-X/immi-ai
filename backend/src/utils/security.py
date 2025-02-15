import re
from typing import Tuple, Set
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class RateLimitConfig:
    max_requests: int
    time_window: timedelta
    
class SecurityManager:
    """Handles security and compliance features"""
    
    def __init__(self):
        self.rate_limits = {}
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'passport': r'\b[A-Z]\d{8}\b'
        }
    
    def check_for_pii(self, text: str) -> Tuple[bool, Set[str]]:
        """Check for PII in text"""
        found_pii = set()
        for pii_type, pattern in self.pii_patterns.items():
            if re.search(pattern, text):
                found_pii.add(pii_type)
        return bool(found_pii), found_pii
    
    def mask_pii(self, text: str) -> str:
        """Mask any PII found in text"""
        masked_text = text
        for pii_type, pattern in self.pii_patterns.items():
            masked_text = re.sub(pattern, f"[MASKED_{pii_type.upper()}]", masked_text)
        return masked_text
    
    def check_rate_limit(self, user_id: str, config: RateLimitConfig) -> bool:
        """Check if user has exceeded rate limit"""
        now = datetime.now()
        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = []
        
        # Clean old requests
        self.rate_limits[user_id] = [
            timestamp for timestamp in self.rate_limits[user_id]
            if now - timestamp < config.time_window
        ]
        
        # Check limit
        if len(self.rate_limits[user_id]) >= config.max_requests:
            return False
        
        # Add new request
        self.rate_limits[user_id].append(now)
        return True 