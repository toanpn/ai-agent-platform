from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class HRBot:
    """
    HR department bot for handling human resources related queries.
    """
    
    def __init__(self):
        self.name = "HR Bot"
        self.department = "Human Resources"
        
        # Common HR responses and knowledge base
        self.hr_knowledge = {
            "pto": {
                "keywords": ["pto", "vacation", "time off", "holiday", "sick leave"],
                "response": """Regarding Paid Time Off (PTO):

• New employees accrue 15 days of PTO annually
• PTO requests should be submitted at least 2 weeks in advance
• Maximum carryover is 5 days to the next year
• Sick leave is separate from vacation time
• For extended illness, please contact HR for FMLA information

Would you like me to help you submit a PTO request or check your balance?"""
            },
            "benefits": {
                "keywords": ["benefits", "health insurance", "401k", "retirement", "dental", "vision"],
                "response": """Our comprehensive benefits package includes:

• Health Insurance: Company covers 80% of premiums
• Dental & Vision: Available with employee contribution
• 401(k): 4% company match, immediate vesting
• Life Insurance: 2x annual salary provided
• Flexible Spending Account (FSA) available
• Employee Assistance Program (EAP)

Open enrollment is in November. Would you like details about any specific benefit?"""
            },
            "payroll": {
                "keywords": ["payroll", "salary", "pay", "paycheck", "direct deposit"],
                "response": """Payroll Information:

• Pay periods: Bi-weekly (every other Friday)
• Direct deposit setup: Contact payroll@company.com
• W-2 forms available online in January
• Pay stubs accessible through employee portal
• Questions about deductions: Contact HR

For immediate payroll issues, please contact our payroll department directly."""
            },
            "policies": {
                "keywords": ["policy", "handbook", "code of conduct", "dress code", "remote work"],
                "response": """Company Policies & Employee Handbook:

• Employee handbook is available on the company portal
• Dress code: Business casual, casual Fridays
• Remote work: Hybrid schedule available by department
• Code of conduct: Zero tolerance for harassment
• Training requirements: Annual compliance training

The employee handbook is updated annually. Would you like me to direct you to specific policies?"""
            }
        }
    
    async def process_message(self, message: str, history: List[Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process HR-related messages and provide appropriate responses.
        """
        try:
            # Find the best matching HR topic
            topic = self._find_best_topic(message)
            
            if topic:
                response_data = self.hr_knowledge[topic]
                return {
                    "content": response_data["response"],
                    "agent_name": self.name,
                    "metadata": {
                        "department": self.department,
                        "topic": topic,
                        "confidence": self._calculate_confidence(message, topic)
                    }
                }
            else:
                # General HR response for unmatched queries
                return {
                    "content": f"""Hi! I'm your HR assistant. I can help you with:

• Paid Time Off (PTO) and vacation requests
• Benefits information (health, dental, 401k)
• Payroll and salary questions  
• Company policies and employee handbook
• Performance reviews and training
• General HR procedures

Based on your question: "{message[:100]}...", I'm not sure of the exact information you need. Could you please be more specific about which HR topic you'd like help with?

You can also contact our HR department directly at hr@company.com or extension 1234.""",
                    "agent_name": self.name,
                    "metadata": {
                        "department": self.department,
                        "topic": "general",
                        "requires_clarification": True
                    }
                }
                
        except Exception as e:
            logger.error(f"Error in HR bot: {str(e)}")
            return {
                "content": "I apologize, but I encountered an error while processing your HR request. "
                          "Please contact the HR department directly at hr@company.com or extension 1234.",
                "agent_name": self.name,
                "metadata": {"error": str(e)}
            }
    
    def _find_best_topic(self, message: str) -> str:
        """
        Find the best matching HR topic based on keywords.
        """
        message_lower = message.lower()
        best_topic = None
        max_matches = 0
        
        for topic, data in self.hr_knowledge.items():
            matches = sum(1 for keyword in data["keywords"] if keyword in message_lower)
            if matches > max_matches:
                max_matches = matches
                best_topic = topic
        
        return best_topic if max_matches > 0 else None
    
    def _calculate_confidence(self, message: str, topic: str) -> float:
        """
        Calculate confidence score for topic matching.
        """
        if topic not in self.hr_knowledge:
            return 0.0
            
        message_lower = message.lower()
        keywords = self.hr_knowledge[topic]["keywords"]
        matches = sum(1 for keyword in keywords if keyword in message_lower)
        
        confidence = min(matches / len(keywords), 1.0)
        return round(confidence, 2) 