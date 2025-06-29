"""
Prompt Enhancer Module

This module enhances a raw user query through a four-stage process.
It uses a LLM to classify the intent, extract key entities, and generate a user-facing prompt.
The enhanced prompt is then used to route the request to the most appropriate agent.
"""

import json
from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI


async def enhance_prompt_async(query: str, agent_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhances a raw user query through a four-stage process.

    Args:
        query: The raw user query.
        agent_info: Information about available agents, including names and descriptions.

    Returns:
        The enhanced, structured prompt as a dictionary with:
        - assigned_agents: a list of selected agent names
        - summary: a plain explanation of what the user likely wants
        - key_details_extracted: bullet-point list of extracted fields
        - original_user_query: raw query
        - user_facing_prompt: rewritten, polite sentence for chatbot UI
    """
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

        # Stage 1: Intent Classification
        intents = await _classify_intents(llm, query, agent_info)

        # Stage 2: Entity Extraction
        entities = await _extract_entities(llm, query, intents)

        # Stage 3: Generate User-Facing Prompt
        user_facing_prompt = await _generate_user_facing_prompt(llm, query, intents, entities)

        # Stage 4: Create Final Structure
        enhanced_prompt = _create_final_structure(query, intents, entities, user_facing_prompt)

        return enhanced_prompt

    except Exception as e:
        print(f"Error during prompt enhancement: {e}")
        # Fallback to original query on error
        return {
            "assigned_agents": ["General Assistant"],
            "summary": "Unable to process the request due to an error.",
            "key_details_extracted": "No specific entities were extracted from the query.",
            "original_user_query": query,
            "user_facing_prompt": query,
            "error": "Could not enhance prompt.",
            "details": str(e)
        }


async def _classify_intents(llm: ChatGoogleGenerativeAI, query: str, agent_info: Dict[str, Any]) -> List[str]:
    """Classifies user intents based on available agents, allowing for multiple selections."""
    
    agents = agent_info.get("agents", [])
    if not agents:
        return ["General Assistant"]

    agent_descriptions = "\n".join([f"- **{agent['name']}**: {agent['description']}" for agent in agents])
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """You are an expert intent classifier in a multi-agent assistant system.
Your job is to read a user's query and identify **all the agents** that may be required to handle the request.

IMPORTANT:
- Your output MUST be a JSON array of agent names. For example: ["Agent1", "Agent2"]
- If only one agent is relevant, return an array with a single name: ["Agent1"]
- If you are uncertain or the query is general, return `["General Assistant"]`.
- Do NOT explain your reasoning. Your output should only be the JSON array.

Available agents:
{agent_descriptions}

Classify the intent of the following user query and return a JSON array of agent names."""),
        ("human", "{query}")
    ])
    
    chain = prompt_template | llm
    result = await chain.ainvoke({"query": query, "agent_descriptions": agent_descriptions})
    
    response_content = _extract_content_from_response(result)
    cleaned_json = _clean_json_response(response_content)
    
    try:
        intents = json.loads(cleaned_json)
        if not isinstance(intents, list):
            intents = ["General Assistant"]
    except json.JSONDecodeError:
        valid_agent_names = [agent['name'] for agent in agents]
        intents = [name for name in valid_agent_names if name in response_content]
        if not intents:
            intents = ["General Assistant"]

    valid_agent_names = [agent['name'] for agent in agents]
    validated_intents = [intent for intent in intents if intent in valid_agent_names]
    
    return validated_intents if validated_intents else ["General Assistant"]


async def _extract_entities(llm: ChatGoogleGenerativeAI, query: str, intents: List[str]) -> Dict[str, Any]:
    """Extracts key entities from the query based on the intents."""
    
    intent_str = ", ".join(intents)
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """You are an entity extraction engine.
Your task is to extract key details from a user's query as a structured JSON object.
Use the user's intents to guide what information is important to extract.

Intents: {intents}

Extract relevant entities such as:
- Dates, times, deadlines
- Names, people, contacts
- Locations, departments
- Specific requests or requirements
- Priority levels
- Any other contextually relevant information

Return ONLY a valid JSON object. For example:
{{
    "date": "2024-01-15",
    "department": "HR",
    "type": "leave_request"
}}

If no meaningful entities are found, return an empty JSON object: {{}}
Do not add any explanatory text, markdown formatting, or other content."""),
        ("human", "User Query: {query}")
    ])

    chain = prompt_template | llm
    result = await chain.ainvoke({"query": query, "intents": intent_str})
    
    try:
        response_content = _extract_content_from_response(result)
        response_content = _clean_json_response(response_content)
        entities = json.loads(response_content)
        return entities if isinstance(entities, dict) else {}
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Could not parse entities from LLM response: {e}. Response was: {result}")
        return {}


async def _generate_user_facing_prompt(llm: ChatGoogleGenerativeAI, query: str, intents: List[str], entities: Dict[str, Any]) -> str:
    """Generates a polite, complete sentence suitable for chatbot UI, in Vietnamese."""
    
    intent_str = ", ".join(intents)
    entity_context = ""
    if entities:
        entity_list = [f"{k.replace('_', ' ')}: {v}" for k, v in entities.items()]
        entity_context = f"Key details: {', '.join(entity_list)}"
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """You are a professional communication assistant for an AI agent system.
Your task is to rewrite a user's query into a polite, complete, and well-formed instruction for AI agents.

CRITICAL GUIDELINES:
- If the original query is a command/instruction (like "help read", "analyze", "create", "find", etc.), maintain it as an instruction for the agent to perform
- Do NOT convert instructions into questions asking for guidance
- Make the instruction polite and professional but keep the action-oriented nature
- Ensure it's a complete sentence that clearly tells the agent what to do
- Maintain the original intent and meaning exactly
- Use appropriate business language when applicable
- The result should be a clear directive that an AI agent can act upon

Examples:
- "Hỗ trợ đọc ticket jira" → "Vui lòng hỗ trợ tôi đọc và phân tích các ticket trong Jira."
- "Tạo báo cáo" → "Vui lòng tạo báo cáo chi tiết."
- "Tìm thông tin khách hàng" → "Vui lòng tìm kiếm thông tin khách hàng liên quan."

Agent Context: {intents}
{entity_context}

Rewrite the following query into a single, polite instruction sentence in Vietnamese that tells the agent what action to perform. Return ONLY the rewritten sentence with no additional text or formatting."""),
        ("human", "Original query: {query}")
    ])

    chain = prompt_template | llm
    result = await chain.ainvoke({
        "query": query, 
        "intents": intent_str,
        "entity_context": entity_context
    })
    
    user_facing_prompt = _extract_content_from_response(result).strip()
    
    # Ensure it ends with appropriate punctuation
    if not user_facing_prompt.endswith(('.', '?', '!')):
        user_facing_prompt += '.'
    
    return user_facing_prompt


def _create_final_structure(query: str, intents: List[str], entities: Dict[str, Any], user_facing_prompt: str) -> Dict[str, Any]:
    """Creates the final structured response."""
    
    # Generate key details extracted
    if entities:
        key_details = "\n".join([f"- **{key.replace('_', ' ').title()}**: {value}" for key, value in entities.items()])
    else:
        key_details = "No specific entities were extracted from the query."
    
    # Generate summary
    summary = _generate_summary(query, intents, entities)
    
    return {
        "assigned_agents": intents,
        "summary": summary,
        "key_details_extracted": key_details,
        "original_user_query": query,
        "user_facing_prompt": user_facing_prompt
    }


def _generate_summary(query: str, intents: List[str], entities: Dict[str, Any]) -> str:
    """Generates a plain explanation of what the user likely wants."""
    if len(intents) > 1:
        intent_str = f"a multi-step task involving {', '.join(intents)}"
    else:
        intent_str = f"a matter related to {intents[0]}"
        
    base = f"The user is asking about {intent_str}."
    
    if entities:
        detail = ", ".join([f"{k.replace('_', ' ')}: {v}" for k, v in entities.items()])
        return f"{base} Key points include: {detail}."
    
    return f"{base} No specific details were identified in the query."


def _extract_content_from_response(result) -> str:
    """Safely extracts content from LLM response, handling different response types."""
    if hasattr(result, 'content'):
        return result.content
    elif isinstance(result, str):
        return result
    else:
        return str(result)


def _clean_json_response(response_content: str) -> str:
    """Cleans markdown formatting from JSON responses."""
    response_content = response_content.strip()
    
    # Handle markdown code blocks
    if response_content.startswith("```json"):
        response_content = response_content[7:-3].strip()
    elif response_content.startswith("```"):
        response_content = response_content[3:-3].strip()
    elif response_content.startswith("`json"):
        response_content = response_content[5:-1].strip()
    elif response_content.startswith("`"):
        response_content = response_content[1:-1].strip()
    
    return response_content