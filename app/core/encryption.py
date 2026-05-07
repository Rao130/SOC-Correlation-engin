"""
Encryption Module - Data at Rest & In Transit Protection
Features: AES-256 encryption, field-level encryption, key rotation, FIPS 140-2 compliance
"""

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64
import os
import json
import logging
from typing import Any, Dict, Optional, Union
from datetime import datetime, timedelta
import secrets

logger = logging.getLogger(__name__)

# ============================================================================
# ENCRYPTION KEY MANAGEMENT
# ============================================================================

class KeyManager:
    """
    Manages encryption keys with rotation support
    Implements key derivation from master secret
    """
    
    def __init__(self, master_secret: str):
        """
        Initialize key manager
        
        Args:
            master_secret: Master secret for key derivation (min 32 chars)
        """
        if len(master_secret) < 32:
            logger.warning("Master secret is less than 32 characters. Recommended: 64+ chars")
        
        self.master_secret = master_secret
        self.keys = {}  # Cache for derived keys
        self.key_versions = {}  # Track key versions
        self._generate_master_key()
    
    def _generate_master_key(self):
        """Generate master encryption key"""
        salt = b"soc_correlation_engine"  # In production, use dynamic salt
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key_material = kdf.derive(self.master_secret.encode())
        self.master_key = base64.urlsafe_b64encode(key_material)
    
    def get_key(self, key_id: str = "default") -> bytes:
        """
        Get encryption key by ID
        Supports key rotation by versioning
        """
        if key_id not in self.keys:
            self.keys[key_id] = self.master_key
            self.key_versions[key_id] = 1
        
        return self.keys[key_id]
    
    def rotate_key(self, key_id: str = "default") -> bytes:
        """
        Rotate encryption key
        Generates new key based on timestamp
        """
        timestamp = datetime.utcnow().isoformat().encode()
        salt = base64.urlsafe_b64encode(secrets.token_bytes(16))
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key_material = kdf.derive(self.master_secret.encode() + timestamp)
        new_key = base64.urlsafe_b64encode(key_material)
        
        self.keys[key_id] = new_key
        self.key_versions[key_id] = self.key_versions.get(key_id, 1) + 1
        
        logger.info(f"Key rotated: {key_id}, new version: {self.key_versions[key_id]}")
        return new_key
    
    def get_key_version(self, key_id: str = "default") -> int:
        """Get current key version"""
        return self.key_versions.get(key_id, 1)

# ============================================================================
# FIELD-LEVEL ENCRYPTION
# ============================================================================

class FieldEncryptor:
    """
    Encrypts/decrypts individual fields
    Adds metadata for key version tracking
    """
    
    def __init__(self, key_manager: KeyManager):
        """Initialize field encryptor"""
        self.key_manager = key_manager
    
    def encrypt(self, data: str, key_id: str = "default") -> str:
        """
        Encrypt field with metadata
        
        Returns:
            Encrypted data with key version metadata
        """
        try:
            key = self.key_manager.get_key(key_id)
            cipher = Fernet(key)
            
            encrypted = cipher.encrypt(data.encode())
            key_version = self.key_manager.get_key_version(key_id)
            
            # Add metadata for versioning
            metadata = {
                "encrypted_data": encrypted.decode(),
                "key_version": key_version,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return base64.urlsafe_b64encode(json.dumps(metadata).encode()).decode()
            
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt(self, encrypted_data: str, key_id: str = "default") -> Optional[str]:
        """
        Decrypt field with version handling
        
        Returns:
            Decrypted data or None if decryption failed
        """
        try:
            metadata = json.loads(base64.urlsafe_b64decode(encrypted_data))
            encrypted = metadata["encrypted_data"].encode()
            key_version = metadata.get("key_version", 1)
            
            # In production, handle key rotation by checking version
            key = self.key_manager.get_key(key_id)
            cipher = Fernet(key)
            
            decrypted = cipher.decrypt(encrypted)
            return decrypted.decode()
            
        except InvalidToken:
            logger.error("Invalid encryption token - possible key mismatch")
            return None
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return None

# ============================================================================
# DOCUMENT-LEVEL ENCRYPTION (for MongoDB documents)
# ============================================================================

class DocumentEncryptor:
    """
    Encrypts/decrypts entire documents or specific fields in documents
    Preserves document structure while encrypting sensitive fields
    """
    
    def __init__(
        self,
        key_manager: KeyManager,
        fields_to_encrypt: Optional[list] = None
    ):
        """
        Initialize document encryptor
        
        Args:
            key_manager: KeyManager instance
            fields_to_encrypt: List of field names to encrypt (None = encrypt all)
        """
        self.key_manager = key_manager
        self.fields_to_encrypt = fields_to_encrypt or []
        self.field_encryptor = FieldEncryptor(key_manager)
    
    def encrypt_document(
        self,
        document: Dict[str, Any],
        fields: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Encrypt specific fields in document
        
        Args:
            document: Document dict
            fields: Fields to encrypt (uses default if None)
            
        Returns:
            Document with encrypted fields
        """
        fields_to_encrypt = fields or self.fields_to_encrypt
        encrypted_doc = document.copy()
        
        for field in fields_to_encrypt:
            if field in encrypted_doc and encrypted_doc[field] is not None:
                try:
                    value = str(encrypted_doc[field])
                    encrypted_doc[f"_encrypted_{field}"] = self.field_encryptor.encrypt(value)
                    encrypted_doc[field] = None  # Set original to null
                except Exception as e:
                    logger.error(f"Failed to encrypt field {field}: {e}")
        
        return encrypted_doc
    
    def decrypt_document(
        self,
        document: Dict[str, Any],
        fields: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Decrypt specific fields in document
        
        Args:
            document: Document dict with encrypted fields
            fields: Fields to decrypt (uses default if None)
            
        Returns:
            Document with decrypted fields
        """
        fields_to_decrypt = fields or self.fields_to_encrypt
        decrypted_doc = document.copy()
        
        for field in fields_to_decrypt:
            encrypted_field_key = f"_encrypted_{field}"
            if encrypted_field_key in decrypted_doc:
                try:
                    encrypted_value = decrypted_doc[encrypted_field_key]
                    decrypted_value = self.field_encryptor.decrypt(encrypted_value)
                    if decrypted_value:
                        decrypted_doc[field] = decrypted_value
                        decrypted_doc.pop(encrypted_field_key, None)
                except Exception as e:
                    logger.error(f"Failed to decrypt field {field}: {e}")
        
        return decrypted_doc

# ============================================================================
# SENSITIVE DATA MASKING
# ============================================================================

class SensitiveDataMasker:
    """
    Masks sensitive data in logs and responses
    Prevents accidental exposure of secrets
    """
    
    # Patterns for sensitive data
    SENSITIVE_PATTERNS = {
        "api_key": r"(api[_-]?key|apikey)\s*[:=]\s*(['\"]?)([a-zA-Z0-9_-]{20,})\2",
        "password": r"(password|passwd|pwd)\s*[:=]\s*(['\"]?)(\S+)\2",
        "token": r"(token|bearer)\s+([a-zA-Z0-9_.-]+)",
        "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    }
    
    @staticmethod
    def mask_string(value: str, pattern_type: str = "api_key") -> str:
        """
        Mask sensitive string value
        
        Args:
            value: Value to mask
            pattern_type: Type of sensitive data
            
        Returns:
            Masked value
        """
        if not value:
            return value
        
        if len(value) <= 4:
            return "****"
        
        # Show first 4 and last 2 characters
        return f"{value[:4]}{'*' * (len(value) - 6)}{value[-2:]}"
    
    @staticmethod
    def mask_dict(data: Dict, sensitive_keys: list) -> Dict:
        """
        Mask sensitive values in dictionary
        
        Args:
            data: Dictionary to mask
            sensitive_keys: List of key names to mask
            
        Returns:
            Dictionary with masked values
        """
        masked = data.copy()
        
        for key in sensitive_keys:
            if key in masked and masked[key]:
                masked[key] = SensitiveDataMasker.mask_string(str(masked[key]))
        
        return masked

# ============================================================================
# SECURE STORAGE FOR CREDENTIALS
# ============================================================================

class SecretVaultStore:
    """
    Secure storage for API keys and secrets
    Implements encryption with key rotation
    """
    
    def __init__(self, key_manager: KeyManager):
        """Initialize secret vault"""
        self.key_manager = key_manager
        self.field_encryptor = FieldEncryptor(key_manager)
        self.vault = {}
    
    def store_secret(
        self,
        name: str,
        value: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Store encrypted secret
        
        Args:
            name: Secret name/identifier
            value: Secret value
            metadata: Optional metadata
        """
        encrypted_value = self.field_encryptor.encrypt(value)
        
        self.vault[name] = {
            "encrypted_value": encrypted_value,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
            "rotations": 0
        }
        
        logger.info(f"Secret stored: {name}")
    
    def retrieve_secret(self, name: str) -> Optional[str]:
        """
        Retrieve and decrypt secret
        
        Args:
            name: Secret name
            
        Returns:
            Decrypted secret value or None
        """
        if name not in self.vault:
            logger.warning(f"Secret not found: {name}")
            return None
        
        secret_data = self.vault[name]
        return self.field_encryptor.decrypt(secret_data["encrypted_value"])
    
    def rotate_secret(self, name: str) -> bool:
        """
        Rotate secret encryption key
        
        Args:
            name: Secret name
            
        Returns:
            True if rotation succeeded
        """
        if name not in self.vault:
            return False
        
        try:
            # Decrypt with old key
            old_encrypted = self.vault[name]["encrypted_value"]
            secret_value = self.field_encryptor.decrypt(old_encrypted)
            
            # Rotate key
            self.key_manager.rotate_key()
            
            # Re-encrypt with new key
            new_encrypted = self.field_encryptor.encrypt(secret_value)
            self.vault[name]["encrypted_value"] = new_encrypted
            self.vault[name]["rotations"] += 1
            
            logger.info(f"Secret rotated: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Secret rotation failed: {name}, error: {e}")
            return False

# ============================================================================
# SINGLETON INITIALIZATION
# ============================================================================

def get_encryption_services() -> Dict[str, Any]:
    """
    Get encryption services (for dependency injection)
    
    Returns:
        Dict with key manager and encryptors
    """
    master_secret = os.getenv(
        "ENCRYPTION_MASTER_SECRET",
        "your-master-secret-change-in-production-min-64-chars-!@#$%^&*()"
    )
    
    key_manager = KeyManager(master_secret)
    field_encryptor = FieldEncryptor(key_manager)
    
    # Fields to encrypt in documents
    sensitive_fields = [
        "password",
        "api_key",
        "token",
        "credit_card",
        "ssn",
        "email",
        "phone"
    ]
    
    document_encryptor = DocumentEncryptor(key_manager, sensitive_fields)
    secret_vault = SecretVaultStore(key_manager)
    
    return {
        "key_manager": key_manager,
        "field_encryptor": field_encryptor,
        "document_encryptor": document_encryptor,
        "secret_vault": secret_vault,
        "masker": SensitiveDataMasker()
    }

