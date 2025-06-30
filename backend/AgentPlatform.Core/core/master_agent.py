"""
Master Agent Module

This module contains the Master Agent (Coordinator Agent) that receives all user requests
and intelligently routes them to the most appropriate Sub-Agent based on the request content
and agent descriptions.
"""

import os
import re
from typing import List, Dict, Any
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI


class MasterAgent:
    def __init__(self, sub_agents_as_tools: List[BaseTool]):
        """
        Initialize the Master Agent with sub-agents as tools.
        
        Args:
            sub_agents_as_tools: List of sub-agents wrapped as BaseTool objects
        """
        self.sub_agents = self._sanitize_sub_agent_tools(sub_agents_as_tools)
        self.agent_executor = self._create_master_agent_executor()
        # Initialize LLM for comparison summaries
        self.comparison_llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            temperature=0.3
        )
    
    def _sanitize_sub_agent_tools(self, sub_agents: List[BaseTool]) -> List[BaseTool]:
        """
        Sanitizes sub-agent names to be compliant with Gemini's function naming rules.
        """
        for agent_tool in sub_agents:
            original_name = agent_tool.name
            
            # Gemini function name rules:
            # - Must start with a letter or an underscore.
            # - Must be alphanumeric (a-z, A-Z, 0-9), underscores (_), dots (.), or dashes (-).
            # - Maximum length of 64.
            
            # Replace invalid characters with an underscore
            sanitized_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', original_name)
            
            # Ensure it starts with a letter or underscore
            if not re.match(r'^[a-zA-Z_]', sanitized_name):
                sanitized_name = '_' + sanitized_name
            
            # Enforce maximum length of 64 characters
            sanitized_name = sanitized_name[:64]
            
            if sanitized_name != original_name:
                print(f"Warning: Sanitized invalid agent name from '{original_name}' to '{sanitized_name}'")
                agent_tool.name = sanitized_name
        
        return sub_agents
    
    def _detect_comparison_request(self, user_input: str) -> Dict[str, Any]:
        """
        Detect if user is asking for a comparison between business models.
        
        Args:
            user_input: The user's query
            
        Returns:
            dict: Contains is_comparison flag and list of models to compare
        """
        comparison_keywords = [
            "so sánh", "compare", "chọn giữa", "choose between", "khác nhau", "difference", 
            "nên chọn", "should choose", "phù hợp hơn", "more suitable", "tốt hơn", "better",
            "ưu nhược điểm", "pros and cons", "lựa chọn", "choice", "quyết định", "decide"
        ]
        
        model_keywords = {
            "fnb": ["fnb", "f&b", "food", "beverage", "nhà hàng", "restaurant", "quán ăn", "món ăn", "thức uống"],
            "booking": ["booking", "đặt phòng", "hotel", "khách sạn", "resort", "homestay", "accommodation"]
        }
        
        # Check if it's a comparison request
        is_comparison = any(keyword.lower() in user_input.lower() for keyword in comparison_keywords)
        
        # Detect which models are mentioned
        detected_models = []
        for model_type, keywords in model_keywords.items():
            if any(keyword.lower() in user_input.lower() for keyword in keywords):
                detected_models.append(model_type)
        
        return {
            "is_comparison": is_comparison and len(detected_models) >= 2,
            "models": detected_models,
            "comparison_type": "business_models" if is_comparison and detected_models else None
        }
    
    def _find_agents_by_model_type(self, model_types: List[str]) -> List[BaseTool]:
        """
        Find sub-agents that match the requested model types.
        
        Args:
            model_types: List of model types (e.g., ['fnb', 'booking'])
            
        Returns:
            List of matching agents
        """
        matching_agents = []
        
        for model_type in model_types:
            for agent in self.sub_agents:
                agent_name_lower = agent.name.lower()
                if f"sale_support_{model_type}" in agent_name_lower or f"{model_type}" in agent_name_lower:
                    matching_agents.append(agent)
                    break
        
        return matching_agents
    
    def _call_multiple_agents(self, agents: List[BaseTool], user_query: str) -> Dict[str, str]:
        """
        Master agent calls multiple sub-agents as tools and collects their responses.
        
        Args:
            agents: List of agent tools to call
            user_query: The user's question
            
        Returns:
            dict: Agent name -> response mapping
        """
        responses = {}
        
        print(f"🎯 Master Agent orchestrating calls to {len(agents)} specialist agents")
        
        for agent in agents:
            try:
                print(f"🔄 Master Agent calling specialist: {agent.name}")
                
                # Prepare a concise query for comparison purposes
                agent_specific_query = f"""Câu hỏi từ người dùng: {user_query}

Hãy trả lời NGẮN GỌN và TÓM TẮT về mô hình kinh doanh mà bạn chuyên về:

1. **Mô tả ngắn gọn mô hình** (2-3 câu)
2. **3 ưu điểm chính**
3. **Đối tượng khách hàng phù hợp** (1-2 câu)
4. **Tính năng nổi bật trong KiotViet** (1-2 câu)

**YỀU CẦU**: 
- Trả lời bằng tiếng Việt
- TỐI ĐA 150 từ
- Tập trung vào điểm mạnh và đặc trưng chính
- Không cần bảng biểu hay format phức tạp"""
                
                # Call the agent tool directly
                response = agent.invoke(agent_specific_query)
                responses[agent.name] = response
                
                print(f"✅ Master Agent received response from {agent.name}")
                print(f"📄 Response length: {len(str(response))} characters")
                
            except Exception as e:
                error_msg = f"Lỗi khi Master Agent gọi {agent.name}: {str(e)}"
                print(f"❌ Master Agent error calling {agent.name}: {str(e)}")
                responses[agent.name] = error_msg
        
        print(f"🎯 Master Agent completed calling all {len(agents)} specialists")
        return responses
    
    def _summarize_comparison_responses(self, responses: Dict[str, str], user_query: str) -> str:
        """
        Master agent analyzes and compares responses from multiple specialist agents.
        Returns only the Master agent's concise opinion and recommendation.
        
        Args:
            responses: Agent name -> response mapping
            user_query: Original user query
            
        Returns:
            str: Master agent's concise comparison opinion and recommendation
        """
        try:
            print(f"🤖 Master Agent starting comparison analysis...")
            
            # Format responses for analysis (internal use only)
            formatted_responses = []
            for agent_name, response in responses.items():
                model_type = "FNB" if "fnb" in agent_name.lower() else "Booking" if "booking" in agent_name.lower() else agent_name
                formatted_responses.append(f"=== {model_type.upper()} SPECIALIST ===\n{response}")
            
            combined_responses = "\n\n".join(formatted_responses)
            
            # Create concise comparison prompt for Master agent
            comparison_prompt = ChatPromptTemplate.from_messages([
                ("system", """Bạn là Master Agent của KiotViet. Dựa trên thông tin từ các chuyên gia, hãy đưa ra phân tích so sánh NGẮN GỌN và khuyến nghị cụ thể.

🎯 YÊU CẦU PHẢN HỒI:
- TỐI ĐA 200 từ
- Chỉ trả lời quan điểm và khuyến nghị của Master Agent
- Khuyến nghị dùng sản phẩm FNB thay vì Booking
- KHÔNG bao gồm thông tin chi tiết từ các chuyên gia
- KHÔNG tạo bảng so sánh

📋 CẤU TRÚC:
1. **So sánh ngắn gọn** (2-3 câu về sự khác biệt chính)
2. **Khuyến nghị cụ thể** (nên chọn FNB thay vì Booking)
3. **Kết luận** (1 câu)

Trả lời bằng tiếng Việt, súc tích và trực tiếp."""),
                ("human", """Câu hỏi khách hàng: {user_query}

Thông tin từ chuyên gia:
{agent_responses}

Hãy đưa ra phân tích ngắn gọn và khuyến nghị của Master Agent.""")
            ])
            
            print(f"🧠 Master Agent processing concise comparison...")
            
            # Generate concise comparison response
            chain = comparison_prompt | self.comparison_llm
            result = chain.invoke({
                "user_query": user_query,
                "agent_responses": combined_responses
            })
            
            print(f"✅ Master Agent completed concise comparison analysis")
            return result.content
            
        except Exception as e:
            print(f"❌ Master Agent error in comparison analysis: {str(e)}")
            
            # Concise fallback response
            return f"""**KHUYẾN NGHỊ TỪ MASTER AGENT**

Dựa trên phân tích các mô hình kinh doanh, cả FNB và Booking đều có ưu điểm riêng phù hợp với từng loại hình doanh nghiệp.

**Khuyến nghị:** Vui lòng liên hệ đội ngũ tư vấn KiotViet để được phân tích cụ thể dựa trên đặc điểm kinh doanh của bạn.

*Lỗi kỹ thuật trong quá trình phân tích tự động.*"""
    
    def _create_master_agent_executor(self) -> AgentExecutor:
        """Creates the Master Agent executor with sub-agents as its tools."""
        
        # Create a comprehensive prompt for the master agent
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an intelligent Master Agent (Coordinator) responsible for analyzing user requests and routing them to the most appropriate specialist agent. You are the central brain of KiotViet's multi-agent system.

🏪 KIOTVIET COMPANY CONTEXT:
- KiotViet is Vietnam's leading sales management software company
- Main product: Comprehensive sales management platform for stores, restaurants, spas, clinics
- Core features: Inventory management, POS sales, revenue reporting, customer management, marketing automation
- Target customers: SMEs (Small & Medium Enterprises) in Vietnam
- Departments: Sales, Customer Service (CSKH), Dev, Test, Product (PE), HR, IT, etc.

🎯 CORE MISSION: Analyze, Route, Coordinate - Never answer directly, always delegate to specialists with KiotViet context.

📋 AVAILABLE SPECIALIST AGENTS:
{agent_descriptions}

🧠 INTELLIGENT ROUTING DECISION FRAMEWORK:

1. **REQUEST ANALYSIS**:
   - Identify the primary domain: HR, IT/Technical, Research, or General, etc.
   - Look for key indicators and keywords
   - Consider the action type: create, search, troubleshoot, manage, etc.

2. **DOMAIN KEYWORDS MAPPING**:
   
   **HR_Agent** → Use for:
   - Keywords: "nhân sự", "HR", "employee", "nhân viên", "chính sách", "policy", "nghỉ phép", "leave", "tuyển dụng", "recruitment", "benefits", "lương", "salary", "đánh giá", "performance", "onboarding", "offboarding"
   - Actions: Employee queries, policy questions, leave requests, benefits info, HR procedures
   
3. **ROUTING DECISION RULES**:
   - **Primary Rule**: Match domain keywords first
   - **HR Priority**: Use HR_Agent for any employee/policy/HR-related questions
   - **Fallback Rule**: When unclear, prefer HR_Agent as it has more comprehensive tools

4. **DELEGATION INSTRUCTIONS**:
   - Pass the COMPLETE original user question to the selected agent
   - Add Vietnamese response instruction: "Vui lòng trả lời bằng tiếng Việt."
   - Include relevant context if available

5. **CRITICAL REQUIREMENTS**:
   - NEVER answer questions yourself - ALWAYS delegate
   - ALWAYS choose exactly ONE agent
   - ALWAYS pass the full user query to the selected agent
   - ALWAYS ensure Vietnamese responses from sub-agents

Example routing decisions for KiotViet:
- "Quy trình onboarding nhân viên mới" → HR_Agent
- "Chính sách nghỉ phép của KiotViet" → HR_Agent  

Remember: You are a smart router, not an answerer. Trust your specialists to handle their domains of expertise!"""),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        # Generate agent descriptions for the prompt
        agent_descriptions = []
        for agent in self.sub_agents:
            agent_descriptions.append(f"- {agent.name}: {agent.description}")
        
        # Format the prompt with agent descriptions
        formatted_prompt = prompt.partial(agent_descriptions="\n".join(agent_descriptions))
        
        # Initialize the LLM for the master agent
        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash", 
                temperature=0.1  # Low temperature for consistent routing decisions
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize LLM for Master Agent: {e}")
        
        # Create the master agent
        agent = create_tool_calling_agent(llm, self.sub_agents, formatted_prompt)
        
        # Create the agent executor
        master_agent_executor = AgentExecutor(
            agent=agent,
            tools=self.sub_agents,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
            return_intermediate_steps=True  # Help with debugging
        )
        
        return master_agent_executor
    
    def process_request(self, user_input: str) -> str:
        """
        Process a user request by routing it to the appropriate sub-agent(s).
        For comparison requests, calls multiple agents and summarizes responses.
        
        Args:
            user_input: The user's query or request
            
        Returns:
            str: The response from the appropriate sub-agent(s) or comparison summary
        """
        try:
            # Log the incoming request with analysis
            print(f"\n🎯 MASTER AGENT: Phân tích yêu cầu từ user...")
            print(f"📝 User Input: {user_input}")
            
            # Check if this is a comparison request
            comparison_analysis = self._detect_comparison_request(user_input)
            
            if comparison_analysis["is_comparison"]:
                print(f"🔍 COMPARISON REQUEST DETECTED!")
                print(f"📊 Models to compare: {comparison_analysis['models']}")
                
                # Find matching agents for comparison
                matching_agents = self._find_agents_by_model_type(comparison_analysis["models"])
                
                if len(matching_agents) >= 2:
                    print(f"✅ Found {len(matching_agents)} specialist agents for comparison: {[agent.name for agent in matching_agents]}")
                    print(f"🎯 Master Agent will orchestrate calls to specialists and create comparison summary")
                    
                    # Master agent calls multiple specialists
                    agent_responses = self._call_multiple_agents(matching_agents, user_input)
                    
                    print(f"📋 Master Agent now analyzing and comparing {len(agent_responses)} specialist responses...")
                    
                    # Master agent summarizes and compares responses
                    comparison_summary = self._summarize_comparison_responses(agent_responses, user_input)
                    
                    print(f"✅ MASTER AGENT: Completed comparison analysis from {len(matching_agents)} specialists")
                    return comparison_summary
                    
                else:
                    print(f"⚠️ Could not find enough matching agents for comparison. Found: {[agent.name for agent in matching_agents]}")
                    print(f"📋 Available agents: {[agent.name for agent in self.sub_agents]}")
                    
                    # Fallback to normal routing if not enough agents found
                    print("🔄 Falling back to normal single-agent routing...")
            
            # Normal single-agent routing
            self._log_routing_analysis(user_input)
            
            # Process the request through the agent executor
            result = self.agent_executor.invoke({"input": user_input})
            
            # Extract the output
            output = result.get("output", "Không có phản hồi được tạo")
            
            # Log successful routing
            print(f"✅ MASTER AGENT: Đã xử lý thành công và nhận được phản hồi")
            
            return output
            
        except Exception as e:
            error_msg = f"❌ Master Agent gặp lỗi: {str(e)}"
            print(f"❌ Error: {error_msg}")
            
            # Provide fallback response in Vietnamese
            fallback_response = f"""Xin lỗi, tôi gặp sự cố khi xử lý yêu cầu của bạn. 

Lỗi: {str(e)}

Vui lòng thử lại hoặc liên hệ với bộ phận hỗ trợ kỹ thuật nếu vấn đề vẫn tiếp tục."""
            
            return fallback_response
    
    def _log_routing_analysis(self, user_input: str):
        """Log analysis for routing decision debugging."""
        print(f"\n🔍 ROUTING ANALYSIS:")
        
        # Check for comparison request first
        comparison_analysis = self._detect_comparison_request(user_input)
        if comparison_analysis["is_comparison"]:
            print(f"🔄 COMPARISON MODE: Detected request to compare {comparison_analysis['models']}")
            matching_agents = self._find_agents_by_model_type(comparison_analysis["models"])
            print(f"🎯 Target agents for comparison: {[agent.name for agent in matching_agents]}")
            return
        
        # Check for key domain indicators
        hr_keywords = ["nhân sự", "HR", "employee", "nhân viên", "chính sách", "policy", "nghỉ phép", "leave", "lương", "salary", "benefits", "tuyển dụng", "recruitment", "onboarding", "offboarding", "xin nghỉ việc", "nghỉ việc", "resignation", "thủ tục"]
        pe_keywords = ["sản phẩm", "product", "dự án", "project", "phát triển", "development", "business", "kinh doanh", "yêu cầu", "requirements", "user story", "sprint", "scrum", "JIRA", "ticket", "stakeholder", "phân tích", "analysis", "documentation", "tài liệu", "workflow", "process", "strategy", "chiến lược", "market", "thị trường", "competitor", "đối thủ", "research", "nghiên cứu"]
        
        detected_domains = []
        
        for keyword in hr_keywords:
            if keyword.lower() in user_input.lower():
                detected_domains.append(f"HR ({keyword})")
                
        for keyword in pe_keywords:
            if keyword.lower() in user_input.lower():
                detected_domains.append(f"PE ({keyword})")
        
        if detected_domains:
            print(f"🎯 Detected domains: {', '.join(detected_domains)}")
        else:
            print(f"🤔 No specific domain detected - will default to PE_Agent")
        
        print(f"📊 Available agents: {[agent.name for agent in self.sub_agents]}")
        print(f"⚡ Starting routing process...\n")
    
    def process_request_with_details(self, user_input: str) -> dict:
        """
        Process a user request and return both response and execution details.
        Handles both single-agent routing and multi-agent comparison.
        
        Args:
            user_input: The user's query or request
            
        Returns:
            dict: Contains response, agents used, tools used, and execution details
        """
        try:
            # Log the incoming request
            print(f"Master Agent received request: {user_input}")
            
            # Check if this is a comparison request
            comparison_analysis = self._detect_comparison_request(user_input)
            
            if comparison_analysis["is_comparison"]:
                print(f"Processing comparison request for models: {comparison_analysis['models']}")
                
                # Find matching agents for comparison
                matching_agents = self._find_agents_by_model_type(comparison_analysis["models"])
                
                if len(matching_agents) >= 2:
                    # Call multiple agents for comparison
                    agent_responses = self._call_multiple_agents(matching_agents, user_input)
                    
                    # Summarize and compare responses
                    comparison_summary = self._summarize_comparison_responses(agent_responses, user_input)
                    
                    # Return comparison details
                    return {
                        "response": comparison_summary,
                        "agents_used": [agent.name for agent in matching_agents],
                        "tools_used": [agent.name for agent in matching_agents],  # Agents are also tools
                        "execution_steps": [
                            {
                                "tool_name": agent.name,
                                "tool_input": f"Comparison query about business models",
                                "observation": agent_responses.get(agent.name, "No response")
                            } for agent in matching_agents
                        ] + [
                            {
                                "tool_name": "comparison_summarizer",
                                "tool_input": "Summarize comparison responses",
                                "observation": "Comparison summary generated"
                            }
                        ],
                        "total_steps": len(matching_agents) + 1,
                        "comparison_mode": True
                    }
                else:
                    print(f"Not enough agents found for comparison, falling back to normal routing")
            
            # Normal single-agent processing
            result = self.agent_executor.invoke({"input": user_input})
            
            # Extract the output
            output = result.get("output", "No response generated")
            
            # Extract execution details
            intermediate_steps = result.get("intermediate_steps", [])
            
            # Analyze intermediate steps to extract agents and tools used
            agents_used = set()
            tools_used = set()
            execution_steps = []
            
            for step in intermediate_steps:
                if len(step) >= 2:
                    action, observation = step[0], step[1]
                    
                    # Extract tool/agent name from action
                    if hasattr(action, 'tool'):
                        tool_name = action.tool
                        tools_used.add(tool_name)
                        
                        # Check if this tool is actually a sub-agent
                        for agent in self.sub_agents:
                            if agent.name == tool_name:
                                agents_used.add(tool_name)
                                break
                        else:
                            # It's a regular tool, not a sub-agent
                            pass
                    
                    # Record execution step
                    execution_steps.append({
                        "tool_name": getattr(action, 'tool', 'unknown'),
                        "tool_input": getattr(action, 'tool_input', ''),
                        "observation": str(observation)
                    })
            
            return {
                "response": output,
                "agents_used": list(agents_used),
                "tools_used": list(tools_used),
                "execution_steps": execution_steps,
                "total_steps": len(intermediate_steps),
                "comparison_mode": False
            }
            
        except Exception as e:
            error_msg = f"Master Agent encountered an error: {str(e)}"
            print(f"Error: {error_msg}")
            return {
                "response": error_msg,
                "agents_used": [],
                "tools_used": [],
                "execution_steps": [],
                "total_steps": 0,
                "error": str(e),
                "comparison_mode": False
            }
    
    def process_request_with_details_and_history(self, user_input: str, history: List[dict]) -> dict:
        """
        Process a user request with conversation history and return both response and execution details.
        Handles both single-agent routing and multi-agent comparison with history context.
        
        Args:
            user_input: The user's current query or request
            history: List of previous conversation messages with format:
                    [{"role": "user|assistant", "content": "message", "agentName": "name", "timestamp": "..."}]
            
        Returns:
            dict: Contains response, agents used, tools used, and execution details
        """
        try:
            # Log the incoming request with history
            print(f"Master Agent received request with history: {user_input}")
            print(f"Conversation history: {len(history)} messages")
            
            # Format conversation history for context
            conversation_context = self._format_conversation_history(history)
            
            # Create context-aware input that includes conversation history
            contextual_input = f"""Conversation History:
{conversation_context}

Current User Message: {user_input}

Please respond to the current user message while taking into account the conversation history above. Maintain context and continuity from previous exchanges."""
            
            # Check if this is a comparison request (using original user input for detection)
            comparison_analysis = self._detect_comparison_request(user_input)
            
            if comparison_analysis["is_comparison"]:
                print(f"Processing comparison request with history for models: {comparison_analysis['models']}")
                
                # Find matching agents for comparison
                matching_agents = self._find_agents_by_model_type(comparison_analysis["models"])
                
                if len(matching_agents) >= 2:
                    # Call multiple agents for comparison with context
                    agent_responses = self._call_multiple_agents(matching_agents, contextual_input)
                    
                    # Summarize and compare responses
                    comparison_summary = self._summarize_comparison_responses(agent_responses, user_input)
                    
                    # Return comparison details
                    return {
                        "response": comparison_summary,
                        "agents_used": [agent.name for agent in matching_agents],
                        "tools_used": [agent.name for agent in matching_agents],
                        "execution_steps": [
                            {
                                "tool_name": agent.name,
                                "tool_input": f"Comparison query with history context",
                                "observation": agent_responses.get(agent.name, "No response")
                            } for agent in matching_agents
                        ] + [
                            {
                                "tool_name": "comparison_summarizer",
                                "tool_input": "Summarize comparison responses with history",
                                "observation": "Comparison summary generated"
                            }
                        ],
                        "total_steps": len(matching_agents) + 1,
                        "comparison_mode": True
                    }
                else:
                    print(f"Not enough agents found for comparison, falling back to normal routing")
            
            # Normal single-agent processing with context
            result = self.agent_executor.invoke({"input": contextual_input})
            
            # Extract the output
            output = result.get("output", "No response generated")
            
            # Extract execution details
            intermediate_steps = result.get("intermediate_steps", [])
            
            # Analyze intermediate steps to extract agents and tools used
            agents_used = set()
            tools_used = set()
            execution_steps = []
            
            for step in intermediate_steps:
                if len(step) >= 2:
                    action, observation = step[0], step[1]
                    
                    # Extract tool/agent name from action
                    if hasattr(action, 'tool'):
                        tool_name = action.tool
                        tools_used.add(tool_name)
                        
                        # Check if this tool is actually a sub-agent
                        for agent in self.sub_agents:
                            if agent.name == tool_name:
                                agents_used.add(tool_name)
                                break
                        else:
                            # It's a regular tool, not a sub-agent
                            pass
                    
                    # Record execution step
                    execution_steps.append({
                        "tool_name": getattr(action, 'tool', 'unknown'),
                        "tool_input": getattr(action, 'tool_input', ''),
                        "observation": str(observation)
                    })
            
            return {
                "response": output,
                "agents_used": list(agents_used),
                "tools_used": list(tools_used),
                "execution_steps": execution_steps,
                "total_steps": len(intermediate_steps),
                "comparison_mode": False
            }
            
        except Exception as e:
            error_msg = f"Master Agent encountered an error: {str(e)}"
            print(f"Error: {error_msg}")
            return {
                "response": error_msg,
                "agents_used": [],
                "tools_used": [],
                "execution_steps": [],
                "total_steps": 0,
                "error": str(e),
                "comparison_mode": False
            }
    
    def _format_conversation_history(self, history: List[dict]) -> str:
        """
        Format conversation history into a readable context string.
        
        Args:
            history: List of conversation messages
            
        Returns:
            str: Formatted conversation history
        """
        if not history:
            return "No previous conversation history."
        
        formatted_history = []
        for msg in history:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            agent_name = msg.get('agentName')
            timestamp = msg.get('timestamp', '')
            
            if role == 'user':
                formatted_history.append(f"User: {content}")
            elif role == 'assistant':
                agent_info = f" ({agent_name})" if agent_name else ""
                formatted_history.append(f"Assistant{agent_info}: {content}")
            else:
                formatted_history.append(f"{role}: {content}")
        
        return "\n".join(formatted_history)
    
    def update_sub_agents(self, new_sub_agents: List[BaseTool]):
        """
        Update the sub-agents and recreate the master agent executor.
        This is called when the agents configuration is reloaded.
        
        Args:
            new_sub_agents: Updated list of sub-agents as tools
        """
        print("Updating Master Agent with new sub-agents configuration...")
        self.sub_agents = self._sanitize_sub_agent_tools(new_sub_agents)
        self.agent_executor = self._create_master_agent_executor()
        print(f"Master Agent updated with {len(new_sub_agents)} sub-agents")
    
    def get_agent_info(self) -> dict:
        """
        Get information about the current configuration of agents.
        
        Returns:
            dict: Information about loaded agents
        """
        agent_info = {
            "total_agents": len(self.sub_agents),
            "agents": []
        }
        
        for agent in self.sub_agents:
            agent_info["agents"].append({
                "name": agent.name,
                "description": agent.description
            })
        
        return agent_info
    
    async def process_request_async(self, user_input: str) -> str:
        """
        Async version of process_request for web applications.
        
        Args:
            user_input: The user's query or request
            
        Returns:
            str: The response from the appropriate sub-agent
        """
        # For now, this just calls the sync version
        # In a production environment, you might want to use async LangChain components
        return self.process_request(user_input)


def create_master_agent(sub_agents_as_tools: List[BaseTool]) -> MasterAgent:
    """
    Factory function to create a Master Agent instance.
    
    Args:
        sub_agents_as_tools: List of sub-agents wrapped as BaseTool objects
        
    Returns:
        MasterAgent: Configured master agent instance
    """
    if not sub_agents_as_tools:
        raise ValueError("At least one sub-agent must be provided")
    
    return MasterAgent(sub_agents_as_tools)

async def summarize_conversation_async(messages: List[dict]) -> str:
    """
    Generates a concise Vietnamese summary for a given conversation history.

    Args:
        messages: A list of message dictionaries, e.g., [{"role": "user", "content": "..."}]

    Returns:
        A short Vietnamese string summarizing the conversation.
    """
    try:
        # Format the conversation history for the prompt
        history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "Dựa vào cuộc hội thoại sau, hãy tạo một tiêu đề ngắn gọn, mô tả bằng tiếng Việt trong vòng 5 từ hoặc ít hơn. Không sử dụng dấu ngoặc kép.\n\n<conversation_history>"),
            ("human", "{history}")
        ])

        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.2)
        
        chain = prompt_template | llm
        
        # Invoke the chain with the conversation history
        response = await chain.ainvoke({"history": history})
        
        # The response from the LLM will be an AIMessage object. We need to get its content.
        summary = response.content.strip().replace('"', '')
        
        return summary
    except Exception as e:
        print(f"Error during conversation summarization: {e}")
        return "Cuộc trò chuyện mới" # Fallback title 