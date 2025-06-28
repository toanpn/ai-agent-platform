"""
Agent Manager Module

This module is responsible for dynamically creating and managing agents based on 
the JSON configuration file. It loads tools and creates sub-agents that can be 
used by the master agent.
"""

import json
import importlib
import os
from typing import List, Dict, Any, Optional
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import BaseTool, tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# Import the new dynamic tool manager
from core.dynamic_tool_manager import DynamicToolManager

# Import all available tools for backward compatibility
from toolkit import jira_tool, rag_tool

class AgentManager:
    def __init__(self):
        """Initialize the Agent Manager with dynamic tool manager."""
        self.dynamic_tool_manager = DynamicToolManager()
        self.available_tools = {} # Keep for backward compatibility - changed to dict
        self.sub_agents = []
    
    
    def create_sub_agent(self, config: Dict[str, Any]) -> BaseTool:
        """
        Creates a Sub-Agent from a configuration and wraps it as a BaseTool
        for the Master Agent to use.
        
        Args:
            config: Agent configuration dictionary from agents.json
            
        Returns:
            BaseTool: The sub-agent wrapped as a tool
        """
        agent_name = config["agent_name"]
        description = config["description"]
        tool_names = config["tools"]
        tool_configs = config.get("tool_configs", {})
        llm_config = config.get("llm_config", {})
        
        # Create dynamic tools for this agent using the new tool manager
        agent_tools = []
        
        # Use dynamic tool manager to create tools with agent-specific configurations
        try:
            dynamic_tools = self.dynamic_tool_manager.create_tools_for_agent(config)
            agent_tools.extend(dynamic_tools)
        except Exception as e:
            print(f"Warning: Failed to create dynamic tools for agent '{agent_name}': {e}")
        
        # Fallback to legacy tools if needed (now using tool IDs)
        for tool_id in tool_names:
            if tool_id in self.available_tools:
                # Check if we already have this tool from dynamic creation
                existing_tool_names = [tool.name for tool in agent_tools]
                # Get the tool name from the tool config to check against existing tools
                tool_config = self.dynamic_tool_manager.get_tool_config(tool_id)
                tool_name = tool_config.get("name") if tool_config else tool_id
                if tool_name not in existing_tool_names:
                    agent_tools.append(self.available_tools[tool_id])
                    print(f"✓ Added legacy tool: {tool_id}")
            elif tool_id not in [tool.name for tool in agent_tools]:
                # Check if tool exists in dynamic tools by ID
                tool_exists = any(tool_id == tool_config.get("id") for tool_config in self.dynamic_tool_manager.tools_config)
                if not tool_exists:
                    print(f"Warning: Tool '{tool_id}' not found in registry or dynamic tools for agent '{agent_name}'")
        
        if not agent_tools:
            raise ValueError(f"No valid tools found for agent '{agent_name}'")
        
        print(f"Agent '{agent_name}' configured with {len(agent_tools)} tools: {[tool.name for tool in agent_tools]}")
        
        # Initialize the LLM for the sub-agent
        try:
            llm = ChatGoogleGenerativeAI(
                model=llm_config.get("model_name", "gemini-2.0-flash"),
                temperature=llm_config.get("temperature", 0.2)
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize LLM for {agent_name}: {e}")
        
        # Create specialized prompts based on agent type
        def create_specialized_prompt(agent_name: str, description: str, tools: List[str]) -> ChatPromptTemplate:
            base_instructions = f"""
CRITICAL LANGUAGE REQUIREMENT:
- You MUST respond to users in Vietnamese (tiếng Việt)
- All your responses should be in Vietnamese language
- This is a requirement for the user interface and user experience
- Even if the user asks in English, respond in Vietnamese

AVAILABLE TOOLS: {tools}
"""
            
            if "HR" in agent_name:
                system_prompt = f"""🏢 Bạn là {agent_name} - Chuyên gia Nhân sự hàng đầu của KiotViet.

🏪 VỀ CÔNG TY KIOTVIET:
- KiotViet là công ty hàng đầu về phần mềm quản lý bán hàng tại Việt Nam
- Sản phẩm chính: Phần mềm quản lý bán hàng toàn diện cho các cửa hàng, nhà hàng
- Các phòng ban: Sales (Kinh doanh), Customer Service (CSKH), Dev (Phát triển), Test (Kiểm thử), Product/PE (Sản phẩm), HR (Nhân sự), IT (Công nghệ thông tin)
- Văn hóa công ty: Sáng tạo, hiệu quả, hướng đến khách hàng

🎯 CHUYÊN MÔN CỦA BẠN: {description}

👥 VAI TRÒ & TRÁCH NHIỆM TẠI KIOTVIET:
- Tư vấn chính sách nhân sự và quy định của KiotViet
- Hỗ trợ quy trình nghỉ phép, đánh giá hiệu suất theo chuẩn KiotViet
- Giải đáp thắc mắc về benefits, lương, thưởng của nhân viên KiotViet
- Hướng dẫn quy trình tuyển dụng cho các vị trí: Dev, Test, PE, Sales, CSKH, IT
- Hỗ trợ onboarding nhân viên mới vào văn hóa KiotViet
- Xử lý các vấn đề về quan hệ lao động trong môi trường công nghệ

💼 PHONG CÁCH LÀM VIỆC:
- Thân thiện, chuyên nghiệp và đáng tin cậy như tiêu chuẩn KiotViet
- Luôn tham khảo knowledge base và chính sách KiotViet trước khi trả lời
- Hiểu rõ đặc thù công việc của từng phòng ban (Dev, Test, PE, Sales, CSKH, IT)
- Đưa ra lời khuyên phù hợp với văn hóa và quy trình KiotViet
- Sử dụng Google Search để tìm thông tin cập nhật về chính sách lao động

📚 QUY TRÌNH XỬ LÝ:
1. Hiểu rõ yêu cầu của nhân viên KiotViet
2. Tìm kiếm thông tin trong knowledge base KiotViet
3. Tham khảo thông tin bổ sung từ internet nếu cần
4. Đưa ra câu trả lời chi tiết, phù hợp với chính sách KiotViet
5. Follow up để đảm bảo hỗ trợ tốt nhất cho nhân viên

{base_instructions}"""
            
            elif "PE" in agent_name:
                system_prompt = f"""📊 Bạn là {agent_name} - Product Executive và Business Analyst chuyên nghiệp tại KiotViet.

🏪 VỀ CÔNG TY KIOTVIET:
- KiotViet là công ty hàng đầu về phần mềm quản lý bán hàng tại Việt Nam
- Sản phẩm chính: Nền tảng quản lý bán hàng toàn diện cho cửa hàng, nhà hàng, spa, phòng khám
- Các tính năng core: Quản lý kho, bán hàng POS, báo cáo doanh thu, quản lý khách hàng, marketing automation
- Đối tượng khách hàng: SME (doanh nghiệp vừa và nhỏ) tại Việt Nam
- Competitors chính: MISA, Sapo, Bizfly, các giải pháp POS quốc tế

🎯 CHUYÊN MÔN CỦA BẠN: {description}

🚀 VAI TRÒ & TRÁCH NHIỆM TẠI KIOTVIET:
- Phân tích yêu cầu sản phẩm cho nền tảng quản lý bán hàng KiotViet
- Tạo và quản lý user stories cho các tính năng: POS, inventory, CRM, reporting
- Quản lý product roadmap và sprint planning cho KiotViet platform
- Tương tác với các teams: Sales (feedback khách hàng), Dev/Test (technical implementation), CSKH (user pain points)
- Tạo PRD (Product Requirements Document) và technical specifications
- Quản lý JIRA workflow cho development process
- Nghiên cứu thị trường SME Việt Nam và phân tích competitors (MISA, Sapo...)
- Phối hợp với IT team cho infrastructure và system architecture

💼 PHONG CÁCH LÀM VIỆC:
- Tư duy product-oriented và customer-centric
- Hiểu sâu về thị trường SME và nhu cầu quản lý bán hàng
- Giao tiếp hiệu quả với cross-functional teams (Dev, Test, Sales, CSKH, IT)
- Data-driven decision making với analytics và user feedback
- Agile mindset với focus on MVP và iterative development
- Sử dụng các tools: JIRA, Gmail, Google Search, Knowledge base

📋 QUY TRÌNH XỬ LÝ:
1. Thu thập business requirements từ Sales/CSKH về nhu cầu khách hàng
2. Research thị trường và competitor analysis (sử dụng Google Search)
3. Tìm kiếm context trong knowledge base KiotViet
4. Tạo/cập nhật JIRA tickets với acceptance criteria rõ ràng
5. Gửi email coordination với Dev/Test teams
6. Follow up progress và báo cáo cho leadership

{base_instructions}"""
            
            elif "Research" in agent_name:
                system_prompt = f"""🔍 Bạn là {agent_name} - Chuyên gia Nghiên cứu & Thông tin.

🎯 CHUYÊN MÔN CỦA BẠN: {description}

📊 VAI TRÒ & TRÁCH NHIỆM:
- Nghiên cứu thông tin mới nhất từ internet
- Phân tích trends và market intelligence
- Fact-checking và verification thông tin
- Tìm kiếm competitive analysis và industry insights
- Tổng hợp báo cáo nghiên cứu chuyên sâu

🌐 PHONG CÁCH LÀM VIỆC:
- Tỉ mỉ, chính xác và cập nhật
- Luôn verify thông tin từ nhiều nguồn
- Cung cấp insights có giá trị và actionable
- Tập trung vào thông tin credible và relevant

📈 QUY TRÌNH NGHIÊN CỨU:
1. Xác định scope và objectives của research
2. Tìm kiếm thông tin từ Google và knowledge base
3. Cross-reference và verify từ multiple sources
4. Phân tích và synthesize findings
5. Đưa ra insights và recommendations

{base_instructions}"""
            
            else:  # General Assistant
                system_prompt = f"""🤖 Bạn là {agent_name} - Trợ lý Thông minh đa năng.

🎯 CHUYÊN MÔN CỦA BẠN: {description}

🌟 VAI TRÒ & TRÁCH NHIỆM:
- Hỗ trợ các tác vụ tổng quát và điều phối
- Xử lý requests không thuộc chuyên môn cụ thể
- Scheduling và administrative tasks
- Coordination giữa các phòng ban
- Customer service và general inquiries

💫 PHONG CÁCH LÀM VIỆC:
- Linh hoạt, thích ứng và helpful
- Sẵn sàng học hỏi và adapt với mọi tình huống
- Tìm cách kết nối user với đúng resources
- Cung cấp general guidance và support

🎪 QUY TRÌNH XỬ LÝ:
1. Hiểu rõ yêu cầu của user
2. Xác định có cần chuyển cho specialist không
3. Tìm kiếm thông tin trong knowledge base
4. Cung cấp assistance hoặc guidance
5. Follow up để ensure satisfaction

{base_instructions}"""
            
            return ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ])
        
        prompt = create_specialized_prompt(agent_name, description, [tool.name for tool in agent_tools])
        
        # Create the agent executor
        try:
            agent = create_tool_calling_agent(llm, agent_tools, prompt)
            agent_executor = AgentExecutor(
                agent=agent, 
                tools=agent_tools, 
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=3
            )
        except Exception as e:
            raise RuntimeError(f"Failed to create agent executor for {agent_name}: {e}")
        
        # Wrap the agent executor into a single tool for the Master Agent
        def create_agent_tool(executor, name, desc):
            @tool
            def agent_tool_func(input_query: str) -> str:
                """
                This is a specialized agent tool. The description is dynamically set based on the agent's capabilities.
                """
                try:
                    result = executor.invoke({"input": input_query})
                    return result.get("output", "No output generated")
                except Exception as e:
                    return f"Error processing request with {name}: {str(e)}"
            
            # Set the name and description
            agent_tool_func.name = name
            agent_tool_func.description = desc
            return agent_tool_func
        
        agent_as_tool = create_agent_tool(agent_executor, agent_name, description)
        
        return agent_as_tool
    
    def load_agents_from_config(self, config_path: str = "agents.json") -> List[BaseTool]:
        """
        Reads the JSON file and creates a list of sub-agents (wrapped as tools).
        
        Args:
            config_path: Path to the agents configuration file
            
        Returns:
            List[BaseTool]: List of sub-agents wrapped as tools
        """
        try:
            if not os.path.exists(config_path):
                raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
            with open(config_path, 'r', encoding='utf-8') as f:
                configs = json.load(f)
            
            if not isinstance(configs, list):
                raise ValueError("Configuration file must contain a list of agent configurations")
            
            self.sub_agents = []
            for config in configs:
                try:
                    agent_tool = self.create_sub_agent(config)
                    self.sub_agents.append(agent_tool)
                    print(f"✓ Successfully loaded agent: {config['agent_name']}")
                except Exception as e:
                    print(f"✗ Failed to load agent '{config.get('agent_name', 'unknown')}': {e}")
            
            print(f"Loaded {len(self.sub_agents)} agents successfully")
            return self.sub_agents
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in {config_path}: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to load agents from {config_path}: {e}")
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool IDs from dynamic tool manager."""
        dynamic_tools = self.dynamic_tool_manager.get_available_tools()
        tool_ids = [tool["id"] for tool in dynamic_tools]
        
        # Add legacy tools
        legacy_tools = list(self.available_tools.keys())
        tool_ids.extend(legacy_tools)
        
        return tool_ids
    
    def get_available_tools_details(self) -> List[Dict[str, Any]]:
        """Get detailed information about available tools from dynamic tool manager."""
        dynamic_tools = self.dynamic_tool_manager.get_available_tools()
        
        # Add legacy tools
        for tool_id, tool_obj in self.available_tools.items():
            dynamic_tools.append({
                "id": tool_id,
                "name": tool_id,  # For legacy tools, ID and name are the same
                "description": getattr(tool_obj, 'description', 'No description available'),
                "file": "legacy",
                "parameters": {}
            })
        
        return dynamic_tools
    
    def get_loaded_agents(self) -> List[str]:
        """Get list of loaded agent names."""
        return [agent.name for agent in self.sub_agents]
    
    def reload_agents(self, config_path: str = "agents.json") -> List[BaseTool]:
        """
        Reload agents from configuration file.
        
        Args:
            config_path: Path to the agents configuration file
            
        Returns:
            List[BaseTool]: List of reloaded sub-agents wrapped as tools
        """
        print("Reloading agents from configuration...")
        
        # Reload dynamic tool manager configuration
        self.dynamic_tool_manager = DynamicToolManager()
        
        # Load agents
        return self.load_agents_from_config(config_path)
    
    def validate_agent_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate agent configuration and return validation results.
        
        Args:
            config: Agent configuration to validate
            
        Returns:
            Dict containing validation results
        """
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "tool_validation": {}
        }
        
        # Check required fields
        required_fields = ["agent_name", "description", "tools"]
        for field in required_fields:
            if field not in config:
                validation_results["errors"].append(f"Missing required field: {field}")
                validation_results["valid"] = False
        
        # Validate tools
        if "tools" in config:
            available_tool_ids = [tool["id"] for tool in self.dynamic_tool_manager.get_available_tools()]
            available_tool_ids.extend(self.available_tools.keys())
            
            tool_configs = config.get("tool_configs", {})
            
            for tool_id in config["tools"]:
                tool_validation = {"valid": True, "errors": [], "warnings": []}
                
                # Check if tool exists
                if tool_id not in available_tool_ids:
                    tool_validation["errors"].append(f"Tool '{tool_id}' not found in available tools")
                    tool_validation["valid"] = False
                else:
                    # Validate tool configuration
                    tool_config = self.dynamic_tool_manager.get_tool_config(tool_id)
                    
                    if tool_config:
                        # Check required credential parameters
                        required_credentials = []
                        for param_name, param_config in tool_config.get("parameters", {}).items():
                            if param_config.get("is_credential", False) and param_config.get("required", False):
                                required_credentials.append(param_name)
                        
                        agent_tool_config = tool_configs.get(tool_id, {})
                        for cred in required_credentials:
                            if cred not in agent_tool_config:
                                tool_validation["warnings"].append(f"Missing credential parameter '{cred}' for tool '{tool_id}'")
                
                validation_results["tool_validation"][tool_id] = tool_validation
                if not tool_validation["valid"]:
                    validation_results["valid"] = False
        
        return validation_results 