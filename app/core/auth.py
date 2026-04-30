"""
Authentication Module - Temporary Implementation
"""

from typing import Dict, Any

def get_current_user() -> Dict[str, Any]:
    """Temporary dummy authentication function"""
    return {
        "id": "temp_user",
        "username": "demo_user",
        "role": "analyst",
        "permissions": ["read", "write"]
    }
