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
        - assigned_agent: the selected agent name
        - summary: a plain explanation of what the user likely wants
        - key_details_extracted: bullet-point list of extracted fields
        - original_user_query: raw query
        - user_facing_prompt: rewritten, polite sentence for chatbot UI
    """
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

        # Stage 1: Intent Classification
        intent = await _classify_intent(llm, query, agent_info)

        # Stage 2: Entity Extraction
        entities = await _extract_entities(llm, query, intent)

        # Stage 3: Generate User-Facing Prompt
        user_facing_prompt = await _generate_user_facing_prompt(llm, query, intent, entities)

        # Stage 4: Create Final Structure
        enhanced_prompt = _create_final_structure(query, intent, entities, user_facing_prompt)

        return enhanced_prompt

    except Exception as e:
        print(f"Error during prompt enhancement: {e}")
        # Fallback to original query on error
        return {
            "assigned_agent": "General Assistant",
            "summary": "Unable to process the request due to an error.",
            "key_details_extracted": "No specific entities were extracted from the query.",
            "original_user_query": query,
            "user_facing_prompt": query,
            "error": "Could not enhance prompt.",
            "details": str(e)
        }


async def _classify_intent(llm: ChatGoogleGenerativeAI, query: str, agent_info: Dict[str, Any]) -> str:
    """Classifies user intent based on available agents."""
    
    agents = agent_info.get("agents", [])
    if not agents:
        return "General Assistant"

    agent_descriptions = "\n".join([f"- **{agent['name']}**: {agent['description']}" for agent in agents])
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """You are an expert intent classifier in a multi-agent assistant system. 
Your job is to read a user's query and match it to the **most appropriate agent** that can handle the request.

IMPORTANT:
- You MUST return only the exact name of one agent from the list below.
- If you are uncertain, return the name of the agent that seems most closely related.
- Do NOT explain your reasoning. Your output should only be the agent's name.

Available agents:
{agent_descriptions}

Classify the intent of the following user query and return ONLY the agent name."""),
        ("human", "{query}")
    ])
    
    chain = prompt_template | llm
    result = await chain.ainvoke({"query": query, "agent_descriptions": agent_descriptions})
    
    intent = _extract_content_from_response(result).strip()
    
    # Validate the intent against available agents
    valid_agent_names = [agent['name'] for agent in agents]
    if intent not in valid_agent_names:
        # Fallback logic: find the best match or default
        best_match = next((name for name in valid_agent_names if name.lower() in intent.lower()), None)
        if best_match:
            intent = best_match
        else:
            intent = valid_agent_names[0] if valid_agent_names else "General Assistant"

    return intent


async def _extract_entities(llm: ChatGoogleGenerativeAI, query: str, intent: str) -> Dict[str, Any]:
    """Extracts key entities from the query based on the intent."""
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """You are an entity extraction engine.
Your task is to extract key details from a user's query as a structured JSON object.
Use the user's intent to guide what information is important to extract.

Intent: {intent}

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
    result = await chain.ainvoke({"query": query, "intent": intent})
    
    try:
        response_content = _extract_content_from_response(result)
        response_content = _clean_json_response(response_content)
        entities = json.loads(response_content)
        return entities if isinstance(entities, dict) else {}
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Could not parse entities from LLM response: {e}. Response was: {result}")
        return {}


async def _generate_user_facing_prompt(llm: ChatGoogleGenerativeAI, query: str, intent: str, entities: Dict[str, Any]) -> str:
    """Generates a polite, complete sentence suitable for chatbot UI."""
    
    entity_context = ""
    if entities:
        entity_list = [f"{k.replace('_', ' ')}: {v}" for k, v in entities.items()]
        entity_context = f"Key details: {', '.join(entity_list)}"
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """You are a professional communication assistant.
Your task is to rewrite a user's query into a polite, complete, and well-formed sentence suitable for a chatbot interface.

Guidelines:
- Make the request polite and professional
- Ensure it's a complete sentence
- Keep it concise but clear
- Maintain the original intent and meaning
- Use appropriate business language when applicable

Agent Context: {intent}
{entity_context}

Rewrite the following query into a single, polite sentence. Return ONLY the rewritten sentence with no additional text or formatting."""),
        ("human", "Original query: {query}")
    ])

    chain = prompt_template | llm
    result = await chain.ainvoke({
        "query": query, 
        "intent": intent,
        "entity_context": entity_context
    })
    
    user_facing_prompt = _extract_content_from_response(result).strip()
    
    # Ensure it ends with appropriate punctuation
    if not user_facing_prompt.endswith(('.', '?', '!')):
        user_facing_prompt += '.'
    
    return user_facing_prompt


def _create_final_structure(query: str, intent: str, entities: Dict[str, Any], user_facing_prompt: str) -> Dict[str, Any]:
    """Creates the final structured response."""
    
    # Generate key details extracted
    if entities:
        key_details = "\n".join([f"- **{key.replace('_', ' ').title()}**: {value}" for key, value in entities.items()])
    else:
        key_details = "No specific entities were extracted from the query."
    
    # Generate summary
    summary = _generate_summary(query, intent, entities)
    
    return {
        "assigned_agent": intent,
        "summary": summary,
        "key_details_extracted": key_details,
        "original_user_query": query,
        "user_facing_prompt": user_facing_prompt
    }


def _generate_summary(query: str, intent: str, entities: Dict[str, Any]) -> str:
    """Generates a plain explanation of what the user likely wants."""
    base = f"The user is asking about a matter related to {intent.replace('_', ' ')}."
    
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