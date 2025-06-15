"""
Google ADK Configuration for AgentPlatform.Core
This file configures ADK runtime and deployment settings.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ADKConfig:
    """
    Configuration class for Google ADK integration.
    """
    
    # Google API Configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")
    
    # ADK Runtime Configuration
    ADK_RUNTIME_CONFIG = {
        "model": "gemini-pro",
        "temperature": 0.7,
        "max_tokens": 2048,
        "timeout": 60,
        "retry_attempts": 3,
        "streaming": False
    }
    
    # Agent Configuration
    AGENT_CONFIG = {
        "max_agents_per_workflow": 10,
        "agent_timeout": 120,
        "enable_memory": True,
        "memory_type": "session",
        "enable_callbacks": True
    }
    
    # Tool Configuration
    TOOL_CONFIG = {
        "enable_builtin_tools": True,
        "builtin_tools": {
            "search": True,
            "file_operations": True,
            "http": True,
            "code_execution": False  # Disabled for security
        },
        "tool_timeout": 30,
        "max_concurrent_tools": 5
    }
    
    # Multi-Agent Configuration
    MULTI_AGENT_CONFIG = {
        "default_orchestration": "sequential",
        "enable_parallel": True,
        "enable_loop": True,
        "max_workflow_depth": 5,
        "workflow_timeout": 300
    }
    
    # Database Configuration (keep existing)
    DATABASE_CONFIG = {
        "connection_string": os.getenv("DATABASE_URL"),
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30
    }
    
    # Deployment Configuration
    DEPLOYMENT_CONFIG = {
        "environment": os.getenv("ENVIRONMENT", "development"),
        "debug": os.getenv("DEBUG", "false").lower() == "true",
        "host": os.getenv("API_HOST", "0.0.0.0"),
        "port": int(os.getenv("API_PORT", "8000")),
        "workers": int(os.getenv("WORKERS", "4"))
    }
    
    # Logging Configuration
    LOGGING_CONFIG = {
        "level": os.getenv("LOG_LEVEL", "INFO"),
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "adk_agent_platform.log",
        "max_bytes": 10485760,  # 10MB
        "backup_count": 5
    }
    
    # Security Configuration
    SECURITY_CONFIG = {
        "enable_auth": os.getenv("ENABLE_AUTH", "false").lower() == "true",
        "jwt_secret": os.getenv("JWT_SECRET"),
        "jwt_algorithm": "HS256",
        "jwt_expiration": 3600,  # 1 hour
        "cors_origins": os.getenv("CORS_ORIGINS", "*").split(",")
    }
    
    @classmethod
    def get_adk_runtime_config(cls) -> Dict[str, Any]:
        """
        Get ADK runtime configuration.
        
        Returns:
            Dict[str, Any]: Runtime configuration
        """
        return {
            **cls.ADK_RUNTIME_CONFIG,
            "api_key": cls.GOOGLE_API_KEY,
            "project_id": cls.GOOGLE_PROJECT_ID
        }
    
    @classmethod
    def get_agent_config(cls) -> Dict[str, Any]:
        """
        Get agent configuration.
        
        Returns:
            Dict[str, Any]: Agent configuration
        """
        return cls.AGENT_CONFIG
    
    @classmethod
    def get_tool_config(cls) -> Dict[str, Any]:
        """
        Get tool configuration.
        
        Returns:
            Dict[str, Any]: Tool configuration
        """
        return cls.TOOL_CONFIG
    
    @classmethod
    def get_multi_agent_config(cls) -> Dict[str, Any]:
        """
        Get multi-agent configuration.
        
        Returns:
            Dict[str, Any]: Multi-agent configuration
        """
        return cls.MULTI_AGENT_CONFIG
    
    @classmethod
    def validate_config(cls) -> bool:
        """
        Validate configuration settings.
        
        Returns:
            bool: True if configuration is valid
        """
        required_settings = [
            cls.GOOGLE_API_KEY,
            cls.DATABASE_CONFIG["connection_string"]
        ]
        
        missing_settings = [setting for setting in required_settings if not setting]
        
        if missing_settings:
            print(f"Missing required configuration: {missing_settings}")
            return False
        
        return True
    
    @classmethod
    def get_deployment_config(cls) -> Dict[str, Any]:
        """
        Get deployment configuration for ADK.
        
        Returns:
            Dict[str, Any]: Deployment configuration
        """
        return cls.DEPLOYMENT_CONFIG


# Environment-specific configurations
def get_environment_config() -> Dict[str, Any]:
    """
    Get environment-specific configuration.
    
    Returns:
        Dict[str, Any]: Environment configuration
    """
    env = os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        return {
            "debug": False,
            "log_level": "WARNING",
            "enable_cors": False,
            "secure_cookies": True,
            "ssl_required": True
        }
    elif env == "staging":
        return {
            "debug": False,
            "log_level": "INFO",
            "enable_cors": True,
            "secure_cookies": True,
            "ssl_required": True
        }
    else:  # development
        return {
            "debug": True,
            "log_level": "DEBUG",
            "enable_cors": True,
            "secure_cookies": False,
            "ssl_required": False
        }


# ADK-specific deployment configurations
ADK_DEPLOYMENT_CONFIGS = {
    "vertex_ai_agent_engine": {
        "runtime": "vertex-ai",
        "region": os.getenv("GOOGLE_CLOUD_REGION", "us-central1"),
        "scaling": {
            "min_instances": 1,
            "max_instances": 10,
            "concurrency": 100
        }
    },
    "cloud_run": {
        "runtime": "cloud-run",  
        "region": os.getenv("GOOGLE_CLOUD_REGION", "us-central1"),
        "memory": "2Gi",
        "cpu": "2",
        "timeout": 300,
        "scaling": {
            "min_instances": 0,
            "max_instances": 100,
            "concurrency": 1000
        }
    },
    "gke": {
        "runtime": "gke",
        "cluster_name": os.getenv("GKE_CLUSTER_NAME"),
        "namespace": "agent-platform",
        "replicas": 3,
        "resources": {
            "requests": {
                "memory": "1Gi",
                "cpu": "500m"
            },
            "limits": {
                "memory": "2Gi", 
                "cpu": "1000m"
            }
        }
    }
} 