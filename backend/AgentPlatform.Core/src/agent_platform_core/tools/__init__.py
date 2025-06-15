"""
Tools package for Agent Platform Core with Google ADK integration.

This package contains:
- ADK Tools Adapter (adk_tools.py) - Bridges custom tools with Google ADK
- Tool Registry (registry.py) - Central registration for tool discovery
- Business Logic Tools:
  - Jira Integration (jira.py)
  - Google Calendar Integration (google_calendar.py) 
  - Confluence Integration (confluence.py)
- Common Utilities (common/) - Shared HTTP client for legacy tools

Note: Google Search functionality is now provided by ADK's built-in SearchTool.
For new tools, use ADK's built-in tools through the adk_tools adapter.
""" 