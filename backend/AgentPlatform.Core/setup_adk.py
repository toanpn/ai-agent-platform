#!/usr/bin/env python3
"""
Setup script for Google ADK integration with AgentPlatform.Core
This script helps initialize the ADK environment and configuration.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from adk_config import ADKConfig

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ADKSetup:
    """
    Setup utility for Google ADK integration.
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.src_path = self.project_root / "src"
        
    def validate_environment(self) -> bool:
        """
        Validate that the environment is ready for ADK.
        
        Returns:
            bool: True if environment is valid
        """
        logger.info("Validating environment for Google ADK...")
        
        # Check Python version
        if sys.version_info < (3, 10):
            logger.error("Python 3.10+ is required for Google ADK")
            return False
        
        # Check required environment variables
        required_vars = [
            "GOOGLE_API_KEY",
            "DATABASE_URL"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            logger.info("Please set these variables in your .env file or environment")
            return False
        
        # Validate ADK configuration
        if not ADKConfig.validate_config():
            logger.error("ADK configuration validation failed")
            return False
        
        logger.info("Environment validation successful")
        return True
    
    def install_dependencies(self) -> bool:
        """
        Install required dependencies for ADK.
        
        Returns:
            bool: True if installation successful
        """
        logger.info("Installing Google ADK dependencies...")
        
        try:
            # Install/upgrade Google ADK
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", "google-adk"
            ], check=True)
            
            # Install other dependencies
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], check=True)
            
            logger.info("Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e}")
            return False
    
    def setup_adk_directories(self) -> bool:
        """
        Create necessary directories for ADK.
        
        Returns:
            bool: True if setup successful
        """
        logger.info("Setting up ADK directories...")
        
        directories = [
            self.project_root / "logs",
            self.project_root / "uploads",
            self.project_root / "tmp",
            self.src_path / "agent_platform_core" / "agents" / "workflows",
            self.src_path / "agent_platform_core" / "tools" / "custom"
        ]
        
        try:
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {directory}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create directories: {e}")
            return False
    
    def create_sample_agents(self) -> bool:
        """
        Create sample ADK agents for testing.
        
        Returns:
            bool: True if creation successful
        """
        logger.info("Creating sample ADK agents...")
        
        sample_agent_code = '''"""
Sample ADK agent for testing AgentPlatform.Core integration.
"""

from adk import LlmAgent
from adk.models import GeminiModel
from adk.tools import SearchTool

def create_sample_agent():
    """Create a sample ADK agent."""
    model = GeminiModel("gemini-pro")
    tools = [SearchTool()]
    
    agent = LlmAgent(
        name="Sample Agent",
        model=model,
        system_prompt="You are a helpful AI assistant.",
        tools=tools,
        description="Sample agent for testing"
    )
    
    return agent

if __name__ == "__main__":
    agent = create_sample_agent()
    print(f"Created sample agent: {agent.name}")
'''
        
        try:
            sample_file = self.src_path / "agent_platform_core" / "agents" / "sample_adk_agent.py"
            sample_file.write_text(sample_agent_code)
            logger.info(f"Created sample agent: {sample_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create sample agents: {e}")
            return False
    
    def test_adk_integration(self) -> bool:
        """
        Test ADK integration.
        
        Returns:
            bool: True if test successful
        """
        logger.info("Testing ADK integration...")
        
        try:
            # Test ADK imports
            from adk import LlmAgent
            from adk.models import GeminiModel
            from adk.tools import Tool
            
            logger.info("ADK imports successful")
            
            # Test configuration
            config = ADKConfig.get_adk_runtime_config()
            if not config.get("api_key"):
                logger.error("Google API key not configured")
                return False
            
            logger.info("ADK integration test passed")
            return True
            
        except ImportError as e:
            logger.error(f"ADK import failed: {e}")
            return False
        except Exception as e:
            logger.error(f"ADK integration test failed: {e}")
            return False
    
    def create_env_template(self) -> bool:
        """
        Create .env template file.
        
        Returns:
            bool: True if creation successful
        """
        logger.info("Creating .env template...")
        
        env_template = '''# Google ADK Configuration
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_PROJECT_ID=your_google_project_id_here
GOOGLE_CLOUD_REGION=us-central1

# Database Configuration
DATABASE_URL=mssql+pyodbc://sa:YourStrong@Passw0rd@localhost:1433/agentplatform?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes

# Application Configuration
ENVIRONMENT=development
DEBUG=true
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# Tool Credentials
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your_jira_username
JIRA_API_TOKEN=your_jira_api_token

CONFLUENCE_URL=https://your-domain.atlassian.net/wiki
CONFLUENCE_USERNAME=your_confluence_username
CONFLUENCE_API_TOKEN=your_confluence_api_token

GOOGLE_CALENDAR_CREDENTIALS_FILE=path/to/credentials.json
GOOGLE_CALENDAR_TOKEN_FILE=path/to/token.json

# Security Configuration
ENABLE_AUTH=false
JWT_SECRET=your_jwt_secret_here
CORS_ORIGINS=*

# Deployment Configuration
WORKERS=4
'''
        
        try:
            env_file = self.project_root / ".env.template"
            env_file.write_text(env_template)
            logger.info(f"Created .env template: {env_file}")
            
            if not (self.project_root / ".env").exists():
                (self.project_root / ".env").write_text(env_template)
                logger.info("Created .env file from template")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create .env template: {e}")
            return False
    
    def run_setup(self) -> bool:
        """
        Run the complete ADK setup process.
        
        Returns:
            bool: True if setup successful
        """
        logger.info("Starting Google ADK setup for AgentPlatform.Core...")
        
        steps = [
            ("Validating environment", self.validate_environment),
            ("Installing dependencies", self.install_dependencies),
            ("Setting up directories", self.setup_adk_directories),
            ("Creating sample agents", self.create_sample_agents),
            ("Creating env template", self.create_env_template),
            ("Testing ADK integration", self.test_adk_integration)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"Running step: {step_name}")
            if not step_func():
                logger.error(f"Setup failed at step: {step_name}")
                return False
            logger.info(f"Step completed: {step_name}")
        
        logger.info("Google ADK setup completed successfully!")
        logger.info("Next steps:")
        logger.info("1. Configure your .env file with the required credentials")
        logger.info("2. Start the application: python -m uvicorn agent_platform_core.main:app --reload")
        logger.info("3. Test the ADK integration at: http://localhost:8000/docs")
        
        return True


def main():
    """Main entry point for the setup script."""
    setup = ADKSetup()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "validate":
            success = setup.validate_environment()
        elif command == "install":
            success = setup.install_dependencies()
        elif command == "test":
            success = setup.test_adk_integration()
        elif command == "directories":
            success = setup.setup_adk_directories()
        elif command == "sample":
            success = setup.create_sample_agents()
        elif command == "env":
            success = setup.create_env_template()
        else:
            logger.error(f"Unknown command: {command}")
            success = False
    else:
        success = setup.run_setup()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 