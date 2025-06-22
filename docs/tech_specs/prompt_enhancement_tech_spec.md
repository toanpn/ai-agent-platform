# Prompt Enhancement Technical Specification for the Dynamic Multi-Agent System

## 1. Introduction

This document outlines a proposed solution to enhance and standardize user prompts before they are processed by the `MasterAgent`. The goal is to improve the accuracy of task routing to the appropriate sub-agent, reduce ambiguity, and create a more robust and reliable system.

The core problem in any multi-agent system is ensuring the user's request is correctly understood and delegated. A vague query like "it's not working" provides little information for a router agent. By "enhancing" the prompt, we can transform it into a structured, information-rich query that directly aligns with the capabilities of the specialist sub-agents.

## 2. Current Architecture Overview

The system currently employs a two-layer hierarchical agent architecture:

*   **Layer 1: The `MasterAgent` (Router)**: This agent's sole responsibility is to receive a user's query and delegate it to the most suitable sub-agent. Its decision-making is based on matching the user's query to the `name` and `description` of the available sub-agents.
*   **Layer 2: The `Sub-Agents` (Specialists)**: These are defined in `agents.json` and are designed for specific tasks (e.g., `IT_Support_Agent`, `HR_Agent`). Each has a dedicated set of tools and a focused purpose.

The effectiveness of this entire system hinges on the `MasterAgent`'s ability to make the correct routing decision. This can fail if the user's input is ambiguous or does not clearly map to a sub-agent's description.

## 3. Proposed Solution: The "Prompt Enhancer" Module

I propose the introduction of a new conceptual module called the **"Prompt Enhancer"**. This module will act as a pre-processing step, taking the raw user input and transforming it into a structured, enhanced prompt before it reaches the `MasterAgent`.

The Prompt Enhancer operates in three stages:

### Stage 1: Intent Classification

The first step is to determine the user's primary *intent*. The possible intents should directly correspond to the available sub-agents.

*   **Input**: Raw user query (e.g., "My computer is super slow and I can't open Jira.").
*   **Process**: Use a powerful LLM with a carefully crafted system prompt to classify the input into one of the predefined categories. These categories are derived from your `agents.json` file.
*   **Output**: A single intent string (e.g., `IT_Support`).

**Example LLM System Prompt for Intent Classification:**

```
You are an expert intent classifier for a multi-agent system. Your task is to analyze a user's query and determine which agent is best suited to handle it. Respond with ONLY the agent's name.

Here are the available agents and their descriptions:

- **IT_Support_Agent**: Handles technical support, software/hardware issues, and Jira problems.
- **HR_Agent**: Answers questions about HR policies, leave, and recruitment.
- **Search_Agent**: Performs general internet searches for news, facts, or general questions.
- **General_Utility_Agent**: Handles miscellaneous tasks like calendar checks and weather.
- **ADK_Assistant**: Handles advanced tasks using ADK tools.

Based on the user's query, which agent should be chosen? Only return the agent's name.
```

### Stage 2: Entity Extraction

Once the intent is known, the next step is to extract key pieces of information (entities) from the query that are relevant to that intent.

*   **Input**: Raw user query + the identified intent (`IT_Support`).
*   **Process**: Based on the intent, use an LLM to extract relevant entities. The types of entities to look for depend on the intent.
    *   For `IT_Support`: `device`, `problem_description`, `application`.
    *   For `HR`: `policy_topic`, `document_type`, `date_range`.
*   **Output**: A structured object (e.g., a JSON object) containing the extracted entities.
    *   `{ "device": "computer", "problem": "slow performance", "application": "Jira" }`

### Stage 3: Prompt Rewriting/Structuring

The final step is to combine the original query, the intent, and the extracted entities into a new, highly-structured prompt.

*   **Input**: Original query, intent, and extracted entities.
*   **Process**: Use an LLM or even a simple template engine to generate a new prompt.
*   **Output**: The enhanced prompt that will be sent to the `MasterAgent`.

**Example of a Rewritten, Enhanced Prompt:**

```
User is requesting assistance from the IT_Support_Agent.

**Summary of Request**: The user's computer is experiencing slow performance, which is preventing them from using the 'Jira' application.

**Extracted Details**:
- **Device**: computer
- **Problem**: slow performance
- **Application Affected**: Jira

**Original Query**: "My computer is super slow and I can't open Jira."
```

## 4. Example End-to-End Workflow

| Step                                         | Example                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| -------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1. User Input in UI**                      | A user types into a text area in the web interface: "I need to know what the company's policy is on working from home."                                                                                                                                                                                                                                                                                                                                                                        |
| **2. User Initiates Enhancement**            | The user clicks the "Enhance" button next to the input field.                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| **3. UI to `AgentPlatform.API`**             | The UI client sends the raw query to an endpoint on the `AgentPlatform.API` (e.g., `POST /api/enhance-prompt`).                                                                                                                                                                                                                                                                                                                                                                                  |
| **4. `AgentPlatform.API` to `core api_server`** | The `AgentPlatform.API` acts as a gateway and forwards the request to the Python-based `core api_server`, which hosts the actual enhancement logic.                                                                                                                                                                                                                                                                                                                                             |
| **5. Prompt Enhancer Execution**             | *   **Intent Classification:** Identifies `HR_Agent`. <br> *   **Entity Extraction:** Extracts `{ "policy_topic": "work from home" }`. <br> *   **Prompt Rewriting:** Creates a new prompt: <br> `User is asking an HR-related question. \n**Topic:** Company policy \n**Subject:** Remote work / work from home. \n**Request:** Please retrieve the official policy document regarding working from home.`                                                                                               |
| **6. Enhanced Prompt Returned to UI**        | The `core api_server` returns the structured text to `AgentPlatform.API`, which then forwards it back to the UI client.                                                                                                                                                                                                                                                                                                                                                                        |
| **7. User Submits for Processing**           | The UI displays the enhanced prompt, potentially in a read-only or editable text area. The user reviews it and clicks "Submit" to send it for processing by the agent system.                                                                                                                                                                                                                                                                                                                     |
| **8. To MasterAgent**                        | The UI sends the final, enhanced prompt to be processed. This request goes through `AgentPlatform.API` to the `MasterAgent`.                                                                                                                                                                                                                                                                                                                                                                    |
| **9. MasterAgent Routing**                   | The prompt is now unambiguous. The `MasterAgent` can easily and accurately route this to the `HR_Agent`, as its description is: *"Useful for questions about HR policies, leave procedures, and recruitment information."*                                                                                                                                                                                                                                                                          |


## 5. Benefits of this Approach

*   **Improved Routing Accuracy**: The structured prompt makes it trivial for the `MasterAgent` to choose the correct sub-agent.
*   **Enhanced Reliability**: Reduces the chances of the agent failing due to ambiguous input.
*   **Better User Experience**: The system will feel more intelligent and will be less likely to ask clarifying questions or make mistakes.
*   **Scalability**: As more agents are added, this structured approach ensures the system remains manageable and routing remains accurate.
*   **Debugging**: When routing fails, the enhanced prompt provides a clear log of what the system *thought* the user wanted, making it easier to debug.

## 6. High-Level Integration Plan

The prompt enhancement functionality will be exposed as a dedicated API endpoint. This allows a user to trigger and review the enhancement from a UI client before submitting the final prompt for agent processing. The architecture involves a frontend, a backend-for-frontend (BFF), and the core processing server.

### Architectural Flow

1.  **UI Client**: A user enters their raw query and clicks an "Enhance" button. This action triggers an API call to the `AgentPlatform.API`.
2.  **`AgentPlatform.API` (.NET)**: This BFF acts as a secure gateway. It receives the request from the client and forwards it to the `core api_server` for processing.
3.  **`core api_server` (Python)**: This server hosts the prompt enhancement logic. It exposes an endpoint (e.g., `/enhance-prompt`) that performs the three stages (Intent Classification, Entity Extraction, Prompt Rewriting) and returns the final structured prompt text.

### API and Code Examples

#### `AgentPlatform.API` (Enhancement Controller)

A new controller can be added to handle forwarding the request to the python backend.

```csharp
[ApiController]
[Route("api")]
public class PromptEnhancementController : ControllerBase
{
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly IConfiguration _configuration;

    public PromptEnhancementController(IHttpClientFactory httpClientFactory, IConfiguration configuration)
    {
        _httpClientFactory = httpClientFactory;
        _configuration = configuration;
    }

    [HttpPost("enhance-prompt")]
    public async Task<IActionResult> EnhancePrompt([FromBody] PromptEnhancementRequest request)
    {
        var coreApiUrl = _configuration["CoreApiServerUrl"];
        var client = _httpClientFactory.CreateClient();

        var coreApiRequest = new { query = request.Query };

        // Forward the request to the core api_server
        var response = await client.PostAsJsonAsync($"{coreApiUrl}/enhance-prompt", coreApiRequest);

        if (response.IsSuccessStatusCode)
        {
            var enhancedPrompt = await response.Content.ReadAsStringAsync();
            return Ok(new { enhancedPrompt });
        }

        return StatusCode((int)response.StatusCode, await response.Content.ReadAsStringAsync());
    }
}

public class PromptEnhancementRequest
{
    public string Query { get; set; }
}
```

#### `core api_server.py` (Enhancement Endpoint)

The existing `api_server.py` will be updated to include a specific endpoint for enhancement.

```python
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
# ... other necessary imports

app = FastAPI()

# You would have a way to access your system_manager and agents
# system_manager = SystemManager() 
# system_manager.load_agents()

class EnhanceRequest(BaseModel):
    query: str

@app.post("/enhance-prompt", response_class=PlainTextResponse)
async def enhance_prompt_endpoint(request: EnhanceRequest):
    """
    Receives a raw user query, enhances it, and returns the structured result.
    """
    # Assuming agent info is needed for enhancement
    agent_info = system_manager.master_agent.get_agent_info()
    
    # Call the core enhancement logic
    enhanced_prompt_text = await enhance_prompt_async(request.query, agent_info)

    # Return the pure text response
    return PlainTextResponse(content=enhanced_prompt_text)

# The /process endpoint would remain to handle the final, enhanced prompt
@app.post("/process")
async def process_request_endpoint(request: ProcessRequest):
    # ... logic to process the final prompt with the MasterAgent
    response = await system_manager.master_agent.process_request_async(request.enhanced_prompt)
    return {"response": response}

```

This concludes the proposal for the Prompt Enhancement module. 