"""
Main Application Entry Point

This module serves as the entry point for the Dynamic Multi-Agent System.
It handles:
1. Initial loading of agents from configuration
2. File monitoring for automatic agent reloading
3. User interaction interface
4. Integration of all system components
"""

import os
import sys
import time
import asyncio
from typing import Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv

# Import our custom modules
from core.agent_manager import AgentManager
from core.master_agent import MasterAgent, create_master_agent

# Load environment variables
load_dotenv()

class AgentConfigHandler(FileSystemEventHandler):
    """Handles file system events for the agents configuration file."""
    
    def __init__(self, system_manager: 'AgentSystemManager'):
        self.system_manager = system_manager
        self.last_modified = 0
        
    def on_modified(self, event):
        """Called when the agents.json file is modified."""
        if event.is_directory:
            return
            
        # Check if it's the agents.json file
        if event.src_path.endswith('agents.json'):
            # Prevent multiple rapid reloads
            current_time = time.time()
            if current_time - self.last_modified < 2:  # 2 second cooldown
                return
            self.last_modified = current_time
            
            print(f"\n📁 Configuration file changed: {event.src_path}")
            print("🔄 Reloading agents...")
            
            try:
                self.system_manager.reload_system()
                print("✅ System reloaded successfully!")
            except Exception as e:
                print(f"❌ Failed to reload system: {e}")


class AgentSystemManager:
    """Manages the overall agent system including loading, reloading, and coordination."""
    
    def __init__(self, config_path: str = "agents.json"):
        self.config_path = config_path
        self.agent_manager = AgentManager()
        self.master_agent: Optional[MasterAgent] = None
        self.observer: Optional[Observer] = None
        
    def initialize_system(self):
        """Initialize the agent system with initial configuration."""
        try:
            print("🚀 Initializing Dynamic Multi-Agent System...")
            
            # Check if Google API key is available
            if not os.getenv('GOOGLE_API_KEY'):
                print("❌ Error: GOOGLE_API_KEY not found in environment variables.")
                print("   Please set your Google API key in a .env file or environment variable.")
                print("   The system requires an API key to function properly.")
                sys.exit(1)
            
            # Load agents from configuration
            sub_agents = self.agent_manager.load_agents_from_config(self.config_path)
            
            if not sub_agents:
                raise RuntimeError("No agents could be loaded from configuration")
            
            # Create master agent
            self.master_agent = create_master_agent(sub_agents)
            
            print(f"✅ System initialized with {len(sub_agents)} agents")
            
            # Display loaded agents
            self._display_system_info()
            
        except Exception as e:
            print(f"❌ Failed to initialize system: {e}")
            sys.exit(1)
    
    def start_file_monitoring(self):
        """Start monitoring the configuration file for changes."""
        try:
            # Set up file monitoring
            self.observer = Observer()
            event_handler = AgentConfigHandler(self)
            
            # Monitor the current directory for agents.json changes
            self.observer.schedule(event_handler, path='.', recursive=False)
            self.observer.start()
            
            print("👁️  File monitoring started - agents.json changes will trigger automatic reload")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not start file monitoring: {e}")
    
    def reload_system(self):
        """Reload the entire agent system with new configuration."""
        try:
            # Reload agents
            new_sub_agents = self.agent_manager.reload_agents(self.config_path)
            
            if not new_sub_agents:
                print("⚠️  No agents loaded after reload - keeping existing configuration")
                return
            
            # Update master agent
            if self.master_agent:
                self.master_agent.update_sub_agents(new_sub_agents)
            else:
                self.master_agent = create_master_agent(new_sub_agents)
            
            self._display_system_info()
            
        except Exception as e:
            print(f"❌ Error during system reload: {e}")
            raise
    
    def _display_system_info(self):
        """Display information about the current system configuration."""
        if not self.master_agent:
            return
            
        agent_info = self.master_agent.get_agent_info()
        
        print("\n" + "="*60)
        print("📋 SYSTEM CONFIGURATION")
        print("="*60)
        print(f"Total Agents: {agent_info['total_agents']}")
        print("\nLoaded Agents:")
        
        for agent in agent_info['agents']:
            print(f"  🤖 {agent['name']}")
            print(f"     {agent['description'][:80]}{'...' if len(agent['description']) > 80 else ''}")
        
        print("="*60)
        print("Available Tools:", ", ".join(self.agent_manager.get_available_tools()))
        print("="*60 + "\n")
    
    def process_user_request(self, user_input: str) -> str:
        """Process a user request through the master agent."""
        if not self.master_agent:
            return "❌ System not initialized properly"
        
        try:
            return self.master_agent.process_request(user_input)
        except Exception as e:
            return f"❌ Error processing request: {str(e)}"
    
    def stop_monitoring(self):
        """Stop file monitoring."""
        if self.observer:
            self.observer.stop()
            self.observer.join()


def run_interactive_mode(system_manager: AgentSystemManager):
    """Run the system in interactive command-line mode."""
    print("💬 Interactive mode started. Type 'quit', 'exit', or 'q' to stop.")
    print("   Type 'help' for available commands.")
    print("   Type 'info' to see current system configuration.")
    print("-" * 60)
    
    print("\n🎯 Try these example queries:")
    print("   • 'What's the weather like in New York?'")
    print("   • 'Check my calendar for today'") 
    print("   • 'Search for latest AI news'")
    print("   • 'My computer is running slowly, create a ticket'")
    print("   • 'What's the company policy on remote work?'")
    print("-" * 60)
    
    while True:
        try:
            user_input = input("\n🧑 User: ").strip()
            
            if not user_input:
                continue
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'help':
                print("""
Available commands:
  help     - Show this help message
  info     - Display current system configuration  
  reload   - Manually reload agents configuration
  quit/exit/q - Exit the application
  
Example queries:
  • "What's the weather in London?"
  • "Check my calendar for tomorrow"
  • "Search for Python programming tutorials"
  • "Create a Jira ticket for printer issues"
  • "What's the leave policy?"
                """)
                continue
            elif user_input.lower() == 'info':
                system_manager._display_system_info()
                continue
            elif user_input.lower() == 'reload':
                print("🔄 Manually reloading system...")
                try:
                    system_manager.reload_system()
                    print("✅ System reloaded successfully!")
                except Exception as e:
                    print(f"❌ Failed to reload: {e}")
                continue
            
            # Process user request
            print("\n🤖 Agent: Processing your request...")
            response = system_manager.process_user_request(user_input)
            print(f"\n🤖 Agent: {response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Received interrupt signal. Goodbye!")
            break
        except EOFError:
            print("\n\n👋 End of input. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")


def main():
    """Main application entry point."""
    print("🎯 Dynamic Multi-Agent System Starting...")
    
    # Initialize system manager
    system_manager = AgentSystemManager()
    
    try:
        # Initialize the system
        system_manager.initialize_system()
        
        # Start file monitoring
        system_manager.start_file_monitoring()
        
        # Run interactive mode
        run_interactive_mode(system_manager)
        
    except KeyboardInterrupt:
        print("\n👋 Application interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        # Clean up
        system_manager.stop_monitoring()
        print("🧹 System cleanup completed")


if __name__ == "__main__":
    main() 