from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ITBot:
    """
    IT department bot for handling technical support queries.
    """
    
    def __init__(self):
        self.name = "IT Bot"
        self.department = "Information Technology"
        
        # Common IT responses and knowledge base
        self.it_knowledge = {
            "password": {
                "keywords": ["password", "login", "access", "locked out", "reset", "forgot"],
                "response": """Password and Login Issues:

🔑 **Password Reset Steps:**
1. Go to https://portal.company.com/password-reset
2. Enter your email address
3. Check your email for reset instructions
4. Create a new password (minimum 8 characters with numbers)

🚨 **Account Locked?**
• Accounts lock after 5 failed attempts
• Contact IT helpdesk at ext. 2222 for immediate unlock
• Or email it-support@company.com

**Password Requirements:**
• Minimum 8 characters
• Include uppercase, lowercase, number
• Change every 90 days

Need immediate help? Call IT helpdesk: ext. 2222"""
            },
            "email": {
                "keywords": ["email", "outlook", "mail", "cannot send", "receiving"],
                "response": """Email & Outlook Support:

📧 **Common Email Issues:**

**Can't Send/Receive:**
• Check internet connection
• Restart Outlook application
• Verify email settings: mail.company.com

**Outlook Setup:**
• Server: mail.company.com
• Port: 993 (IMAP) / 587 (SMTP)
• Security: SSL/TLS required

**Mobile Email Setup:**
• iOS: Settings > Mail > Add Account > Exchange
• Android: Gmail app > Add account > Exchange

**Large Attachments:**
• Use company SharePoint for files >25MB
• Access: sharepoint.company.com

Still having issues? Contact IT: it-support@company.com"""
            },
            "hardware": {
                "keywords": ["computer", "laptop", "hardware", "slow", "broken", "screen", "keyboard"],
                "response": """Hardware Support:

💻 **Computer Issues:**

**Slow Performance:**
• Restart your computer daily
• Close unnecessary programs
• Run disk cleanup utility
• Check available storage (need 15%+ free)

**Hardware Problems:**
• Screen issues: Check cable connections first
• Keyboard/mouse: Try different USB port
• Blue screen errors: Note error code and contact IT

**Laptop Issues:**
• Battery not charging: Try different outlet
• Overheating: Ensure vents are clear
• Wi-Fi issues: Restart network adapter

**For Hardware Replacement:**
• Submit ticket at helpdesk.company.com
• Include asset tag number (sticker on device)
• Describe issue in detail

Emergency hardware issues: Call IT ext. 2222"""
            },
            "software": {
                "keywords": ["software", "install", "update", "application", "program", "license"],
                "response": """Software & Applications:

💾 **Software Support:**

**Software Installation:**
• Request via helpdesk.company.com
• Include business justification
• IT will verify licensing and security
• Standard approval time: 1-2 business days

**Updates & Patches:**
• Automatic updates enabled for security
• Reboot when prompted for updates
• Contact IT before disabling updates

**Common Applications:**
• Office 365: Automatically installed
• Antivirus: Defender (managed by IT)
• VPN: FortiClient (download from portal)

**License Issues:**
• "License expired" errors: Contact IT immediately
• Don't install personal software on work devices
• Software requests: Submit business case

Need software help? Email: it-support@company.com"""
            },
            "network": {
                "keywords": ["wifi", "internet", "network", "vpn", "connection", "slow internet"],
                "response": """Network & Connectivity:

🌐 **Network Support:**

**Wi-Fi Issues:**
• Network: CompanyWiFi (password: Welcome2024!)
• Guest network: CompanyGuest (for visitors)
• Restart Wi-Fi adapter if connection fails

**VPN Access:**
• Download FortiClient from company portal
• Use your regular login credentials
• Required for accessing internal systems remotely

**Slow Internet:**
• Speed test: speedtest.company.com
• Expected speeds: 100Mbps+ in office
• Report persistent issues to IT

**Network Drives:**
• Access via \\\\fileserver.company.com
• Map drives through IT portal
• VPN required for remote access

**Connectivity Troubleshooting:**
1. Check ethernet cable connection
2. Restart network adapter
3. Flush DNS: ipconfig /flushdns
4. Contact IT if issues persist

Network emergency: IT helpdesk ext. 2222"""
            }
        }
    
    async def process_message(self, message: str, history: List[Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process IT-related messages and provide appropriate responses.
        """
        try:
            # Find the best matching IT topic
            topic = self._find_best_topic(message)
            
            if topic:
                response_data = self.it_knowledge[topic]
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
                # General IT response for unmatched queries
                return {
                    "content": f"""Hi! I'm your IT support assistant. I can help you with:

🔧 **Technical Support Areas:**
• Password resets and login issues
• Email and Outlook problems  
• Hardware issues (computers, laptops, printers)
• Software installation and updates
• Network and Wi-Fi connectivity
• VPN setup and access
• Security and antivirus questions

Based on your question: "{message[:100]}...", I'm not sure of the specific technical issue you're experiencing. Could you provide more details about:

• What device/system you're using?
• What error messages you're seeing?
• When the problem started?

**Quick Contact Options:**
• 🆘 Emergency IT support: ext. 2222
• 📧 Email support: it-support@company.com  
• 🎫 Submit ticket: helpdesk.company.com
• 💬 Live chat: Available 8AM-6PM weekdays""",
                    "agent_name": self.name,
                    "metadata": {
                        "department": self.department,
                        "topic": "general",
                        "requires_clarification": True
                    }
                }
                
        except Exception as e:
            logger.error(f"Error in IT bot: {str(e)}")
            return {
                "content": "I apologize, but I encountered a technical error while processing your request. "
                          "Please contact IT support directly:\n\n"
                          "📞 Phone: ext. 2222\n"
                          "📧 Email: it-support@company.com\n"
                          "🎫 Helpdesk: helpdesk.company.com",
                "agent_name": self.name,
                "metadata": {"error": str(e)}
            }
    
    def _find_best_topic(self, message: str) -> str:
        """
        Find the best matching IT topic based on keywords.
        """
        message_lower = message.lower()
        best_topic = None
        max_matches = 0
        
        for topic, data in self.it_knowledge.items():
            matches = sum(1 for keyword in data["keywords"] if keyword in message_lower)
            if matches > max_matches:
                max_matches = matches
                best_topic = topic
        
        return best_topic if max_matches > 0 else None
    
    def _calculate_confidence(self, message: str, topic: str) -> float:
        """
        Calculate confidence score for topic matching.
        """
        if topic not in self.it_knowledge:
            return 0.0
            
        message_lower = message.lower()
        keywords = self.it_knowledge[topic]["keywords"]
        matches = sum(1 for keyword in keywords if keyword in message_lower)
        
        confidence = min(matches / len(keywords), 1.0)
        return round(confidence, 2)