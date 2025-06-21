import os
import requests
from langchain.tools import tool
from typing import Optional

@tool
def jira_ticket_creator(issue_summary: str, issue_description: str, project_key: str = "IT") -> str:
    """
    Creates a new ticket in Jira.
    Use this tool when a user wants to report a new IT issue.
    Returns the ID of the newly created ticket, e.g., 'IT-1234'.
    
    Args:
        issue_summary: Brief title of the issue
        issue_description: Detailed description of the issue
        project_key: Jira project key (defaults to "IT")
    """
    try:
        # Get Jira credentials from environment
        jira_url = os.getenv("JIRA_BASE_URL")
        jira_email = os.getenv("JIRA_EMAIL")
        jira_token = os.getenv("JIRA_API_TOKEN")
        
        if not all([jira_url, jira_email, jira_token]):
            # Mock response for demo purposes
            print(f"Creating Jira ticket in project {project_key} with summary: {issue_summary}")
            new_ticket_id = f"{project_key}-1235"
            return f"Successfully created Jira ticket with ID: {new_ticket_id}"
        
        # Prepare the API request
        url = f"{jira_url}/rest/api/3/issue"
        auth = (jira_email, jira_token)
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": issue_summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "text": issue_description,
                                    "type": "text"
                                }
                            ]
                        }
                    ]
                },
                "issuetype": {"name": "Task"}
            }
        }
        
        response = requests.post(url, json=payload, headers=headers, auth=auth)
        
        if response.status_code == 201:
            ticket_data = response.json()
            ticket_key = ticket_data.get("key")
            return f"Successfully created Jira ticket with ID: {ticket_key}"
        else:
            return f"Failed to create Jira ticket. Status: {response.status_code}, Error: {response.text}"
            
    except Exception as e:
        return f"Error creating Jira ticket: {str(e)}"

@tool
def it_knowledge_base_search(query: str) -> str:
    """
    Searches the IT knowledge base for solutions to common problems.
    Use this to find instruction documents or troubleshooting guides.
    
    Args:
        query: Search query for the knowledge base
    """
    # Mock knowledge base data - in a real implementation, this would search a database
    knowledge_base = {
        "printer": "How to fix printer connection issues: 1. Check cable connections 2. Restart print spooler service 3. Update printer drivers",
        "slow computer": "Computer performance troubleshooting: 1. Check for malware 2. Clear temporary files 3. Check disk space 4. Update drivers",
        "wifi": "WiFi connection issues: 1. Restart router 2. Forget and reconnect to network 3. Update network drivers 4. Check for interference",
        "password": "Password reset procedure: 1. Use self-service portal 2. Contact IT helpdesk 3. Verify identity with security questions",
        "email": "Email configuration: 1. Use IMAP settings 2. Check server settings 3. Verify credentials 4. Test connection"
    }
    
    # Simple keyword matching
    query_lower = query.lower()
    results = []
    
    for topic, solution in knowledge_base.items():
        if topic in query_lower or any(word in query_lower for word in topic.split()):
            results.append(f"Topic: {topic.title()}\nSolution: {solution}")
    
    if results:
        return f"Found {len(results)} relevant articles:\n\n" + "\n\n".join(results)
    else:
        return f"No specific articles found for '{query}'. Please contact IT support for personalized assistance." 