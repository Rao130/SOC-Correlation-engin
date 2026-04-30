"""
Enhanced Authentication Module - Production-Grade Security
Features: JWT with refresh tokens, token rotation, secure password hashing, audit logging
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import jwt
import os
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
import logging
from functools import lru_cache
import secrets
import hashlib
import json
from enum import Enum

logger = logging.getLogger(__name__)

# ============================================================================
# SECURITY CONFIGURATION
# ============================================================================

class TokenType(str, Enum):
    """Token types for different use cases"""
    ACCESS = "access"
    REFRESH = "refresh"
    API_KEY = "api_key"
    SERVICE = "service"

class UserRole(str, Enum):
    """User roles for RBAC"""
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"
    SERVICE = "service"

# Password hashing configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)

# ============================================================================
# MODELS
# ============================================================================

class TokenPayload(BaseModel):
    """JWT token payload structure"""
    sub: str  # Subject (user_id)
    user_id: str
    username: str
    email: Optional[str] = None
    role: str
    permissions: list
    token_type: str
    iat: int  # Issued at
    exp: int  # Expiration
    jti: str  # JWT ID for revocation
    organization: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class TokenResponse(BaseModel):
    """Token response structure"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    expires_at: str

class User(BaseModel):
    """User model"""
    user_id: str
    username: str
    email: EmailStr
    role: UserRole
    permissions: list
    is_active: bool
    is_locked: bool = False
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0

class LoginRequest(BaseModel):
    """Login request"""
    username: str
    password: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

# ============================================================================
# TOKEN MANAGER - Production-Grade JWT Handling
# ============================================================================

class JWTManager:
    """Manages JWT tokens with rotation, refresh, and revocation"""
    
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 15,
        refresh_token_expire_days: int = 7,
        token_rotation_enabled: bool = True
    ):
        """
        Initialize JWT Manager
        
        Args:
            secret_key: Secret key for signing tokens
            algorithm: Algorithm for signing (HS256, RS256)
            access_token_expire_minutes: Access token expiration in minutes
            refresh_token_expire_days: Refresh token expiration in days
            token_rotation_enabled: Enable automatic token rotation
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire = timedelta(minutes=access_token_expire_minutes)
        self.refresh_token_expire = timedelta(days=refresh_token_expire_days)
        self.token_rotation_enabled = token_rotation_enabled
        self.revoked_tokens = set()  # In production, use Redis
        
        # Validate secret key strength
        if len(secret_key) < 32:
            logger.warning("SECRET_KEY is less than 32 characters. Recommended: 64+ characters")
    
    def create_token_pair(
        self,
        user_id: str,
        username: str,
        email: str,
        role: str,
        permissions: list,
        organization: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Create access and refresh token pair
        
        Returns:
            Tuple of (access_token, refresh_token)
        """
        jti = self._generate_jti()
        now = datetime.utcnow()
        
        # Access token payload
        access_payload = {
            "sub": user_id,
            "user_id": user_id,
            "username": username,
            "email": email,
            "role": role,
            "permissions": permissions,
            "token_type": TokenType.ACCESS.value,
            "iat": int(now.timestamp()),
            "exp": int((now + self.access_token_expire).timestamp()),
            "jti": jti,
            "organization": organization,
            "ip_address": ip_address,
            "user_agent": user_agent
        }
        
        # Refresh token payload
        refresh_payload = {
            "sub": user_id,
            "user_id": user_id,
            "username": username,
            "token_type": TokenType.REFRESH.value,
            "iat": int(now.timestamp()),
            "exp": int((now + self.refresh_token_expire).timestamp()),
            "jti": self._generate_jti(),
            "parent_jti": jti  # Link to access token
        }
        
        access_token = jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm=self.algorithm)
        
        # Log token creation
        logger.info(f"Token pair created for user: {username}, JTI: {jti}")
        
        return access_token, refresh_token
    
    def verify_token(self, token: str, token_type: TokenType = TokenType.ACCESS) -> Optional[Dict[str, Any]]:
        """
        Verify and decode token
        
        Args:
            token: Token string
            token_type: Expected token type
            
        Returns:
            Decoded payload or None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token type
            if payload.get("token_type") != token_type.value:
                logger.warning(f"Token type mismatch. Expected: {token_type.value}, Got: {payload.get('token_type')}")
                return None
            
            # Check if token is revoked
            jti = payload.get("jti")
            if jti in self.revoked_tokens:
                logger.warning(f"Token revoked: {jti}")
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    def refresh_access_token(self, refresh_token: str, user_data: Dict[str, Any]) -> Optional[Tuple[str, str]]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Refresh token string
            user_data: Current user data from token
            
        Returns:
            New token pair or None if refresh failed
        """
        payload = self.verify_token(refresh_token, TokenType.REFRESH)
        if not payload:
            return None
        
        # Create new token pair with rotated JTI
        new_access, new_refresh = self.create_token_pair(
            user_id=payload["user_id"],
            username=payload["username"],
            email=user_data.get("email"),
            role=user_data.get("role"),
            permissions=user_data.get("permissions", []),
            organization=payload.get("organization"),
            ip_address=payload.get("ip_address")
        )
        
        # Revoke old refresh token if rotation enabled
        if self.token_rotation_enabled:
            self.revoke_token(payload.get("jti"))
        
        logger.info(f"Token refreshed for user: {payload['username']}")
        return new_access, new_refresh
    
    def revoke_token(self, jti: str) -> None:
        """Revoke token by JTI"""
        self.revoked_tokens.add(jti)
        logger.info(f"Token revoked: {jti}")
    
    def _generate_jti(self) -> str:
        """Generate unique JWT ID"""
        return hashlib.sha256(secrets.token_bytes(32)).hexdigest()[:16]

# ============================================================================
# PASSWORD MANAGER - Secure Password Hashing
# ============================================================================

class PasswordManager:
    """Manages password hashing and validation"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            True if password matches
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, str]:
        """
        Validate password strength
        
        Minimum requirements:
        - 12 characters
        - 1 uppercase
        - 1 lowercase
        - 1 digit
        - 1 special character
        
        Returns:
            (is_valid, message)
        """
        if len(password) < 12:
            return False, "Password must be at least 12 characters long"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is strong"

# ============================================================================
# AUDIT LOGGING - Security Event Tracking
# ============================================================================

class AuditLogger:
    """Logs security-relevant events"""
    
    @staticmethod
    def log_login_attempt(
        username: str,
        success: bool,
        ip_address: Optional[str] = None,
        reason: Optional[str] = None
    ) -> None:
        """Log login attempt"""
        event = {
            "event_type": "LOGIN_ATTEMPT",
            "username": username,
            "success": success,
            "ip_address": ip_address,
            "timestamp": datetime.utcnow().isoformat(),
            "reason": reason
        }
        logger.info(json.dumps(event))
    
    @staticmethod
    def log_token_revocation(
        user_id: str,
        jti: str,
        reason: str = "Logout"
    ) -> None:
        """Log token revocation"""
        event = {
            "event_type": "TOKEN_REVOCATION",
            "user_id": user_id,
            "jti": jti,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
        logger.info(json.dumps(event))
    
    @staticmethod
    def log_permission_change(
        user_id: str,
        old_permissions: list,
        new_permissions: list,
        changed_by: str
    ) -> None:
        """Log permission changes"""
        event = {
            "event_type": "PERMISSION_CHANGE",
            "user_id": user_id,
            "old_permissions": old_permissions,
            "new_permissions": new_permissions,
            "changed_by": changed_by,
            "timestamp": datetime.utcnow().isoformat()
        }
        logger.info(json.dumps(event))

# ============================================================================
# SESSION MANAGER - Track Active Sessions
# ============================================================================

class SessionManager:
    """Manages user sessions with timeout and activity tracking"""
    
    def __init__(self, session_timeout_minutes: int = 30):
        """Initialize session manager"""
        self.sessions = {}  # In production, use Redis
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
    
    def create_session(
        self,
        user_id: str,
        ip_address: str,
        user_agent: str
    ) -> str:
        """Create new session"""
        session_id = secrets.token_urlsafe(32)
        self.sessions[session_id] = {
            "user_id": user_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        }
        logger.info(f"Session created: {session_id} for user: {user_id}")
        return session_id
    
    def validate_session(self, session_id: str) -> bool:
        """Validate session is still active"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        age = datetime.utcnow() - session["last_activity"]
        
        if age > self.session_timeout:
            del self.sessions[session_id]
            return False
        
        # Update last activity
        session["last_activity"] = datetime.utcnow()
        return True
    
    def destroy_session(self, session_id: str) -> None:
        """Destroy session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Session destroyed: {session_id}")

# ============================================================================
# AUTHENTICATION PROVIDER - Main Auth Handler
# ============================================================================

class AuthenticationProvider:
    """Main authentication provider integrating all components"""
    
    def __init__(
        self,
        secret_key: str,
        access_token_expire_minutes: int = 15,
        refresh_token_expire_days: int = 7,
        session_timeout_minutes: int = 30,
        token_rotation_enabled: bool = True
    ):
        """Initialize authentication provider"""
        self.jwt_manager = JWTManager(
            secret_key=secret_key,
            access_token_expire_minutes=access_token_expire_minutes,
            refresh_token_expire_days=refresh_token_expire_days,
            token_rotation_enabled=token_rotation_enabled
        )
        self.password_manager = PasswordManager()
        self.session_manager = SessionManager(session_timeout_minutes)
        self.audit_logger = AuditLogger()
    
    def authenticate_user(
        self,
        username: str,
        password: str,
        user_db: Dict[str, Any],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Optional[TokenResponse]:
        """
        Authenticate user and return token pair
        
        Args:
            username: Username
            password: Plain text password
            user_db: User database lookup function
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            TokenResponse or None if authentication failed
        """
        # Lookup user
        user = user_db.get(username)
        if not user:
            self.audit_logger.log_login_attempt(username, False, ip_address, "User not found")
            return None
        
        # Verify password
        if not self.password_manager.verify_password(password, user.get("password_hash")):
            self.audit_logger.log_login_attempt(username, False, ip_address, "Invalid password")
            return None
        
        # Create token pair
        access_token, refresh_token = self.jwt_manager.create_token_pair(
            user_id=user["user_id"],
            username=username,
            email=user.get("email"),
            role=user.get("role", UserRole.VIEWER.value),
            permissions=user.get("permissions", []),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Log successful login
        self.audit_logger.log_login_attempt(username, True, ip_address, "Successful")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(self.jwt_manager.access_token_expire.total_seconds()),
            expires_at=(datetime.utcnow() + self.jwt_manager.access_token_expire).isoformat()
        )
    
    def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify access token"""
        return self.jwt_manager.verify_token(token, TokenType.ACCESS)
    
    def refresh_token(
        self,
        refresh_token: str,
        user_data: Dict[str, Any]
    ) -> Optional[TokenResponse]:
        """Refresh access token"""
        result = self.jwt_manager.refresh_access_token(refresh_token, user_data)
        if not result:
            return None
        
        access_token, new_refresh_token = result
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=int(self.jwt_manager.access_token_expire.total_seconds()),
            expires_at=(datetime.utcnow() + self.jwt_manager.access_token_expire).isoformat()
        )
    
    def logout(self, token: str, user_id: str) -> None:
        """Logout user - revoke token"""
        try:
            payload = jwt.decode(token, self.jwt_manager.secret_key, algorithms=[self.jwt_manager.algorithm])
            self.jwt_manager.revoke_token(payload.get("jti"))
            self.audit_logger.log_token_revocation(user_id, payload.get("jti"), "User logout")
        except:
            pass

# ============================================================================
# SINGLETON INSTANCES - For FastAPI dependency injection
# ============================================================================

@lru_cache
def get_auth_provider() -> AuthenticationProvider:
    """Get authentication provider instance (cached)"""
    secret_key = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production-min-64-chars-!@#$%^&*()")
    return AuthenticationProvider(
        secret_key=secret_key,
        access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15)),
        refresh_token_expire_days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7)),
        session_timeout_minutes=int(os.getenv("SESSION_TIMEOUT_MINUTES", 30)),
        token_rotation_enabled=os.getenv("TOKEN_ROTATION_ENABLED", "true").lower() == "true"
    )

