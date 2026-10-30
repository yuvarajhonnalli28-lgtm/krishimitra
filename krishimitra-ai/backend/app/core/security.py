# backend/app/core/security.py
import sys
import os
from pathlib import Path

# Add the project root to Python path for direct execution
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import jwt
import bcrypt
import secrets
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from passlib.context import CryptContext
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import settings
try:
    from app.core.config import settings
except ImportError:
    # Fallback settings if config not available
    class Settings:
        SECRET_KEY = "development-secret-key-change-in-production"
        ALGORITHM = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES = 30
        REFRESH_TOKEN_EXPIRE_DAYS = 7
    settings = Settings()

# Password hashing context with bcrypt
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__rounds=12  # Cost factor
)

# Security schemes
security = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# JWT constants
ALGORITHM = getattr(settings, 'ALGORITHM', 'HS256')
SECRET_KEY = getattr(settings, 'SECRET_KEY', 'development-secret-key')
ACCESS_TOKEN_EXPIRE_MINUTES = getattr(settings, 'ACCESS_TOKEN_EXPIRE_MINUTES', 30)
REFRESH_TOKEN_EXPIRE_DAYS = getattr(settings, 'REFRESH_TOKEN_EXPIRE_DAYS', 7)


class SecurityUtils:
    """
    Security utility functions for authentication, encryption, and validation
    """
    
    @staticmethod
    def verify_token(token: str) -> bool:
        """
        Verify a simple token (legacy method)
        """
        if token == "krishimitra-secret":
            return True
        return False
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """
        Create JWT refresh token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """
        Decode and verify JWT token
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    @staticmethod
    def verify_token_dependency(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, Any]:
        """
        FastAPI dependency to verify JWT token
        """
        token = credentials.credentials
        return SecurityUtils.decode_token(token)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt with 72-byte truncation warning
        """
        # Check password length for bcrypt limitation
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            logger.warning(f"Password exceeds 72 bytes ({len(password_bytes)} bytes). Will be truncated by bcrypt.")
            # Option 1: Let bcrypt truncate (silent)
            # Option 2: Raise error (commented out)
            # raise ValueError("Password cannot be longer than 72 bytes")
        
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash
        """
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            return False
    
    @staticmethod
    def hash_password_bcrypt(password: str) -> str:
        """
        Alternative method using raw bcrypt (without passlib)
        """
        # Truncate to 72 bytes if longer
        password_bytes = password.encode('utf-8')[:72]
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password_bcrypt(plain_password: str, hashed_password: str) -> bool:
        """
        Alternative method using raw bcrypt (without passlib)
        """
        try:
            password_bytes = plain_password.encode('utf-8')[:72]
            return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"BCrypt verification error: {str(e)}")
            return False
    
    @staticmethod
    def generate_api_key() -> str:
        """
        Generate a secure API key
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """
        Hash an API key for storage using bcrypt
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(api_key.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_api_key(api_key: str, hashed_key: str) -> bool:
        """
        Verify an API key against its hash
        """
        try:
            return bcrypt.checkpw(api_key.encode('utf-8'), hashed_key.encode('utf-8'))
        except Exception as e:
            logger.error(f"API key verification error: {str(e)}")
            return False
    
    @staticmethod
    def generate_secure_random_string(length: int = 32) -> str:
        """
        Generate a cryptographically secure random string
        """
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def create_password_reset_token(email: str) -> str:
        """
        Create a password reset token
        """
        expire = datetime.utcnow() + timedelta(hours=24)
        to_encode = {"email": email, "exp": expire, "type": "password_reset"}
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def verify_password_reset_token(token: str) -> Optional[str]:
        """
        Verify password reset token and return email
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != "password_reset":
                return None
            return payload.get("email")
        except jwt.PyJWTError:
            return None
    
    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """
        Basic input sanitization
        """
        dangerous_chars = ['<', '>', '"', "'", ';', '--', '/*', '*/']
        for char in dangerous_chars:
            input_str = input_str.replace(char, '')
        return input_str.strip()
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Basic email validation
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        Validate Indian phone number
        """
        import re
        pattern = r'^[6-9]\d{9}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def generate_session_id() -> str:
        """
        Generate a unique session ID
        """
        return secrets.token_urlsafe(16)
    
    @staticmethod
    def create_csrf_token() -> str:
        """
        Create CSRF protection token
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def verify_csrf_token(token: str, stored_token: str) -> bool:
        """
        Verify CSRF token using constant-time comparison
        """
        return hmac.compare_digest(token, stored_token)
    
    @staticmethod
    def mask_email(email: str) -> str:
        """
        Mask email for display
        """
        if not email or '@' not in email:
            return email
        
        local, domain = email.split('@')
        if len(local) <= 2:
            masked_local = local[0] + '*' * len(local[1:])
        else:
            masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
        
        return f"{masked_local}@{domain}"
    
    @staticmethod
    def mask_phone(phone: str) -> str:
        """
        Mask phone number for display
        """
        if not phone or len(phone) < 6:
            return phone
        
        return phone[:3] + '*' * (len(phone) - 6) + phone[-3:]


# Simple functions for backward compatibility
def verify_token(token: str) -> bool:
    return SecurityUtils.verify_token(token)


def create_access_token(data: Dict[str, Any]) -> str:
    return SecurityUtils.create_access_token(data)


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, Any]:
    return SecurityUtils.verify_token_dependency(credentials)


# Rate limiter helper
class RateLimiter:
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, client_id: str, max_requests: int = 100, window_seconds: int = 60) -> bool:
        now = datetime.utcnow()
        
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if (now - req_time).total_seconds() < window_seconds
        ]
        
        if len(self.requests[client_id]) >= max_requests:
            return False
        
        self.requests[client_id].append(now)
        return True


# Test the module with safe passwords
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🔐 Testing Security Module")
    print("="*50)
    
    print(f"\n✅ Module loaded successfully!")
    print(f"📁 Current file: {__file__}")
    print(f"📂 Project root: {project_root}")
    
    # Test JWT
    test_data = {"user_id": "test123", "role": "farmer"}
    token = SecurityUtils.create_access_token(test_data)
    print(f"\n🔑 JWT Token: {token[:30]}...")
    
    # Test password hashing with safe password (less than 72 bytes)
    password = "farmer123"  # This is safe - about 9 bytes
    print(f"\n🔒 Testing with password: '{password}' (length: {len(password.encode('utf-8'))} bytes)")
    
    # Method 1: Using passlib
    try:
        hashed = SecurityUtils.hash_password(password)
        print(f"✅ passlib hash: {hashed[:30]}...")
        print(f"✅ passlib verify: {SecurityUtils.verify_password(password, hashed)}")
    except Exception as e:
        print(f"❌ passlib error: {str(e)}")
    
    # Method 2: Using raw bcrypt (fallback)
    try:
        hashed2 = SecurityUtils.hash_password_bcrypt(password)
        print(f"✅ raw bcrypt hash: {hashed2[:30]}...")
        print(f"✅ raw bcrypt verify: {SecurityUtils.verify_password_bcrypt(password, hashed2)}")
    except Exception as e:
        print(f"❌ raw bcrypt error: {str(e)}")
    
    # Test with a very long password (to demonstrate truncation)
    long_password = "a" * 100  # 100 characters
    print(f"\n🔒 Testing with long password ({len(long_password)} chars)")
    hashed_long = SecurityUtils.hash_password_bcrypt(long_password)
    print(f"✅ Long password hash created successfully")
    print(f"✅ Long password verify: {SecurityUtils.verify_password_bcrypt(long_password, hashed_long)}")
    
    # Test API key
    api_key = SecurityUtils.generate_api_key()
    hashed_key = SecurityUtils.hash_api_key(api_key)
    print(f"\n🔑 API Key: {api_key[:10]}...")
    print(f"✅ API Key verify: {SecurityUtils.verify_api_key(api_key, hashed_key)}")
    
    # Test email validation
    print(f"\n📧 Email validate 'farmer@example.com': {SecurityUtils.validate_email('farmer@example.com')}")
    print(f"📧 Email validate 'invalid-email': {SecurityUtils.validate_email('invalid-email')}")
    
    # Test phone validation
    print(f"\n📱 Phone validate '9876543210': {SecurityUtils.validate_phone('9876543210')}")
    print(f"📱 Phone validate '12345': {SecurityUtils.validate_phone('12345')}")
    
    # Test masking
    print(f"\n👤 Mask email 'farmer@example.com': {SecurityUtils.mask_email('farmer@example.com')}")
    print(f"👤 Mask phone '9876543210': {SecurityUtils.mask_phone('9876543210')}")
    
    print("\n✨ Security module is ready to use!\n")