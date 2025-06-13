from typing import List, Dict, Any
import re
import logging

logger = logging.getLogger(__name__)

class MainRouterAgent:
    """
    Main router agent that analyzes user messages and routes them to 
    appropriate department-specific agents.
    """
    
    def __init__(self):
        self.name = "Router Agent"
        self.department_keywords = {
            "hr": [
                "vacation", "holiday", "time off", "sick leave", "pto", "paid time off",
                "benefits", "health insurance", "401k", "retirement", "salary", "payroll",
                "hiring", "recruitment", "interview", "onboarding", "employee handbook",
                "policy", "policies", "hr", "human resources", "manager", "supervisor",
                "performance review", "training", "development", "resign", "resignation"
            ],
            "it": [
                "computer", "laptop", "software", "hardware", "network", "wifi", "internet",
                "password", "login", "access", "permissions", "vpn", "email", "outlook",
                "teams", "slack", "printer", "print", "server", "database", "backup",
                "security", "antivirus", "firewall", "troubleshoot", "bug", "error",
                "install", "update", "upgrade", "it", "technical", "technology"
            ]
        }
    
    async def process_message(self, message: str, history: List[Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process the incoming message and route to appropriate agent.
        """
        try:
            # Analyze the message to determine the best department
            department = self._analyze_message(message)
            
            if department == "hr":
                return {
                    "content": f"I'm routing your HR-related question to our HR specialist. "
                              f"Please hold on while I connect you...\n\n"
                              f"HR Agent: Hi! I understand you have a question about: {message[:100]}... "
                              f"I'm here to help with all HR-related matters including benefits, "
                              f"time off, policies, and employee services. How can I assist you today?",
                    "agent_name": "HR Bot",
                    "metadata": {
                        "routed_to": "hr",
                        "confidence": self._calculate_confidence(message, "hr")
                    }
                }
            elif department == "it":
                return {
                    "content": f"I'm routing your IT-related question to our IT support specialist. "
                              f"Please hold on while I connect you...\n\n"
                              f"IT Agent: Hello! I see you need technical assistance with: {message[:100]}... "
                              f"I'm here to help with all technology-related issues including software, "
                              f"hardware, network problems, and system access. What seems to be the issue?",
                    "agent_name": "IT Bot",
                    "metadata": {
                        "routed_to": "it",
                        "confidence": self._calculate_confidence(message, "it")
                    }
                }
            else:
                # General response when department can't be determined
                return {
                    "content": f"Hello! I'm the main assistant for our organization. "
                              f"I can help route your question to the right department. "
                              f"Based on your message: '{message}', I'm not entirely sure which "
                              f"department would be best to help you. \n\n"
                              f"Could you please clarify if your question is related to:\n"
                              f"• HR matters (benefits, time off, policies, hiring)\n"
                              f"• IT support (computers, software, network issues)\n"
                              f"• Or something else?\n\n"
                              f"This will help me connect you with the right specialist!",
                    "agent_name": "Router Agent",
                    "metadata": {
                        "routed_to": "general",
                        "requires_clarification": True
                    }
                }
                
        except Exception as e:
            logger.error(f"Error in router agent: {str(e)}")
            return {
                "content": "I apologize, but I encountered an error while processing your request. "
                          "Please try rephrasing your question or contact support directly.",
                "agent_name": "Router Agent",
                "metadata": {"error": str(e)}
            }
    
    def _analyze_message(self, message: str) -> str:
        """
        Analyze the message content to determine the most appropriate department.
        """
        message_lower = message.lower()
        
        # Calculate scores for each department
        hr_score = sum(1 for keyword in self.department_keywords["hr"] 
                      if keyword in message_lower)
        it_score = sum(1 for keyword in self.department_keywords["it"] 
                      if keyword in message_lower)
        
        # Return department with highest score, or "general" if tie/no match
        if hr_score > it_score and hr_score > 0:
            return "hr"
        elif it_score > hr_score and it_score > 0:
            return "it"
        else:
            return "general"
    
    def _calculate_confidence(self, message: str, department: str) -> float:
        """
        Calculate confidence score for department routing decision.
        """
        message_lower = message.lower()
        keywords = self.department_keywords.get(department, [])
        matches = sum(1 for keyword in keywords if keyword in message_lower)
        
        # Simple confidence calculation based on keyword matches
        if len(keywords) == 0:
            return 0.0
        
        confidence = min(matches / 3.0, 1.0)  # Cap at 1.0, scale based on matches
        return round(confidence, 2) 