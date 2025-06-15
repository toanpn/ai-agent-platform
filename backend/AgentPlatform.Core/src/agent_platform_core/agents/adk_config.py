"""
ADK Configuration for Agent Platform Core.
Simple configuration wrapper for Google ADK integration.
"""

import os


class ADKConfig:
    """
    Configuration class for Google ADK integration within the agent platform.
    """
    
    def __init__(self):
        """Initialize ADK configuration."""
        self.runtime_mode = os.getenv("ADK_RUNTIME_MODE", "local")
        self.telemetry_enabled = os.getenv("ADK_TELEMETRY_ENABLED", "true").lower() == "true"
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "")
        self.project_id = os.getenv("GOOGLE_PROJECT_ID", "")
    
    def is_valid(self) -> bool:
        """
        Check if the configuration is valid.
        
        Returns:
            bool: True if configuration is valid
        """
        return bool(self.google_api_key and self.project_id)
    
    def get_model_config(self) -> dict:
        """
        Get model configuration for ADK.
        
        Returns:
            dict: Model configuration
        """
        return {
            "api_key": self.google_api_key,
            "project_id": self.project_id,
            "model_name": "gemini-pro"
        } 