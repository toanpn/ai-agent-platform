import requests
from langchain.tools import tool
from typing import List, Dict
import json

@tool
def internet_search(query: str) -> str:
    """
    Searches the internet for general information.
    Use this tool when you need to find current information or answers to general questions.
    
    Args:
        query: The search query string
    """
    try:
        # Using a simple search API (you can replace with your preferred search service)
        # This is a mock implementation - in production, you'd use Google Search API, Bing API, etc.
        
        # Mock search results for demo
        mock_results = [
            {
                "title": f"Search result for: {query}",
                "snippet": f"This is a comprehensive answer about {query}. Based on current information, here are the key points to consider...",
                "url": "https://example.com/search-result-1"
            },
            {
                "title": f"Latest information about {query}",
                "snippet": f"Recent developments regarding {query} show that experts recommend the following approaches...",
                "url": "https://example.com/search-result-2" 
            },
            {
                "title": f"Guide to {query}",
                "snippet": f"A detailed guide explaining {query} with step-by-step instructions and best practices...",
                "url": "https://example.com/search-result-3"
            }
        ]
        
        # Format results
        formatted_results = []
        for i, result in enumerate(mock_results[:3], 1):
            formatted_results.append(f"{i}. {result['title']}\n   {result['snippet']}\n   URL: {result['url']}")
        
        return f"Search results for '{query}':\n\n" + "\n\n".join(formatted_results)
        
    except Exception as e:
        return f"Error performing internet search: {str(e)}"

@tool
def policy_document_search(query: str) -> str:
    """
    Searches internal policy documents and HR guidelines.
    Use this tool to find information about company policies, procedures, and HR-related questions.
    
    Args:
        query: Search query for policy documents
    """
    # Mock policy database - in real implementation, this would search a document store
    policies = {
        "leave": {
            "title": "Leave Policy",
            "content": "Annual leave: 25 days per year. Sick leave: Up to 30 days with doctor's certificate. Maternity/Paternity leave: 16 weeks paid leave. Leave requests must be submitted 2 weeks in advance through the HR portal."
        },
        "remote work": {
            "title": "Remote Work Policy", 
            "content": "Employees may work remotely up to 3 days per week with manager approval. Home office setup allowance: $500. Required: reliable internet, secure workspace, availability during core hours 9 AM - 3 PM."
        },
        "expense": {
            "title": "Expense Reimbursement Policy",
            "content": "Business expenses must be pre-approved for amounts over $500. Submit receipts within 30 days. Reimbursement processed within 2 weeks. Covered: travel, meals (up to $50/day), equipment, training."
        },
        "performance": {
            "title": "Performance Review Process",
            "content": "Annual reviews conducted in January. Quarterly check-ins with managers. 360-degree feedback process. Performance ratings: Exceeds, Meets, Needs Improvement. Career development plans updated annually."
        },
        "code of conduct": {
            "title": "Code of Conduct",
            "content": "Professional behavior expected at all times. Zero tolerance for harassment or discrimination. Confidentiality of company information. Conflict of interest disclosure required. Report violations to HR."
        }
    }
    
    query_lower = query.lower()
    results = []
    
    for topic, policy in policies.items():
        if topic in query_lower or any(word in query_lower for word in topic.split()):
            results.append(f"Policy: {policy['title']}\nDetails: {policy['content']}")
    
    if results:
        return f"Found {len(results)} relevant policies:\n\n" + "\n\n".join(results)
    else:
        return f"No specific policies found for '{query}'. Please contact HR for more information or check the employee handbook."

@tool  
def leave_request_tool(leave_type: str, start_date: str, end_date: str, reason: str = "") -> str:
    """
    Submits a leave request on behalf of the employee.
    Use this tool when an employee wants to request time off.
    
    Args:
        leave_type: Type of leave (annual, sick, personal, etc.)
        start_date: Start date of leave (YYYY-MM-DD format)
        end_date: End date of leave (YYYY-MM-DD format)
        reason: Optional reason for the leave
    """
    try:
        # Mock leave request submission - in real implementation, this would integrate with HR system
        request_id = f"LR-{hash(f'{leave_type}{start_date}{end_date}') % 10000:04d}"
        
        # Calculate business days (simplified calculation)
        from datetime import datetime
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        days = (end - start).days + 1
        
        return f"""Leave request submitted successfully!
        
Request ID: {request_id}
Leave Type: {leave_type.title()}
Duration: {start_date} to {end_date} ({days} days)
Reason: {reason if reason else "Not specified"}
Status: Pending manager approval

You will receive an email confirmation shortly. Your manager will be notified to review and approve this request."""
        
    except Exception as e:
        return f"Error submitting leave request: {str(e)}. Please contact HR directly." 