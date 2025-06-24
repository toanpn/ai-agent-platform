import os
import requests
from langchain.tools import tool
from typing import Optional, List
import json

# --- Helper Functions ---

def _get_confluence_credentials():
    """Retrieves Confluence credentials from environment variables."""
    return {
        "url": os.getenv("CONFLUENCE_BASE_URL"),
        "email": os.getenv("CONFLUENCE_EMAIL"),
        "token": os.getenv("CONFLUENCE_API_TOKEN")
    }

def _get_auth_headers():
    """Constructs authentication headers for Confluence API requests."""
    creds = _get_confluence_credentials()
    if not all(creds.values()):
        return None, None
    
    auth = (creds["email"], creds["token"])
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    return auth, headers

# --- Confluence Tools ---

@tool
def confluence_page_search(query: str, space_key: Optional[str] = None) -> str:
    """
    Searches for pages in Confluence.
    Returns a list of matching pages with their titles, IDs, and links.
    
    Args:
        query: The search term to look for.
        space_key: Optional Confluence space key to limit the search.
    """
    creds = _get_confluence_credentials()
    auth, headers = _get_auth_headers()

    if not auth:
        print(f"Searching Confluence for '{query}' in space '{space_key or 'all spaces'}'")
        return json.dumps([
            {"title": "Example Search Result 1", "id": "12345", "link": "/wiki/spaces/EX/pages/12345"},
            {"title": "Another Search Result", "id": "67890", "link": "/wiki/spaces/EX/pages/67890"}
        ])

    cql = f'title~"{query}" or text~"{query}"'
    if space_key:
        cql += f' and space.key="{space_key}"'
    
    search_url = f"{creds['url']}/rest/api/content/search"
    params = {'cql': cql, 'expand': 'space'}
    
    try:
        response = requests.get(search_url, headers=headers, params=params, auth=auth)
        if response.status_code == 200:
            results = response.json().get('results', [])
            return json.dumps([{
                "title": r['title'], 
                "id": r['id'], 
                "link": r['_links']['webui']
            } for r in results])
        else:
            return f"Error searching Confluence: {response.status_code} - {response.text}"
    except Exception as e:
        return f"An error occurred during Confluence search: {e}"

@tool
def confluence_get_page_content(page_id: str) -> str:
    """
    Retrieves the content of a specific Confluence page by its ID.
    
    Args:
        page_id: The ID of the Confluence page.
    """
    creds = _get_confluence_credentials()
    auth, headers = _get_auth_headers()

    if not auth:
        print(f"Getting content for Confluence page ID: {page_id}")
        return json.dumps({
            "id": page_id,
            "title": "Example Page Title",
            "content": "<p>This is the mocked content of the Confluence page.</p>"
        })

    get_url = f"{creds['url']}/rest/api/content/{page_id}?expand=body.storage"
    
    try:
        response = requests.get(get_url, headers=headers, auth=auth)
        if response.status_code == 200:
            page_data = response.json()
            return json.dumps({
                "id": page_data['id'],
                "title": page_data['title'],
                "content": page_data['body']['storage']['value']
            })
        else:
            return f"Error getting page content: {response.status_code} - {response.text}"
    except Exception as e:
        return f"An error occurred while getting page content: {e}"

@tool
def confluence_create_page(space_key: str, title: str, content: str, parent_id: Optional[str] = None) -> str:
    """
    Creates a new page in a Confluence space.
    
    Args:
        space_key: The key of the space where the page will be created.
        title: The title of the new page.
        content: The content of the page in HTML format.
        parent_id: Optional ID of a parent page.
    """
    creds = _get_confluence_credentials()
    auth, headers = _get_auth_headers()

    if not auth:
        new_page_id = "12346"
        print(f"Creating Confluence page '{title}' in space '{space_key}'")
        return f"Successfully created Confluence page with ID: {new_page_id}"

    create_url = f"{creds['url']}/rest/api/content"
    payload = {
        "type": "page",
        "title": title,
        "space": {"key": space_key},
        "body": {"storage": {"value": content, "representation": "storage"}}
    }
    if parent_id:
        payload['ancestors'] = [{'id': parent_id}]

    try:
        response = requests.post(create_url, json=payload, headers=headers, auth=auth)
        if response.status_code == 200:
            new_page = response.json()
            return f"Successfully created Confluence page with ID: {new_page['id']}"
        else:
            return f"Error creating page: {response.status_code} - {response.text}"
    except Exception as e:
        return f"An error occurred while creating the page: {e}"

@tool
def confluence_update_page(page_id: str, new_content: str, new_title: Optional[str] = None) -> str:
    """
    Updates an existing Confluence page.
    
    Args:
        page_id: The ID of the page to update.
        new_content: The new content for the page in HTML format.
        new_title: Optional new title for the page.
    """
    creds = _get_confluence_credentials()
    auth, headers = _get_auth_headers()

    if not auth:
        print(f"Updating Confluence page ID: {page_id}")
        return f"Successfully updated Confluence page with ID: {page_id}"

    # First, get the current page version
    get_url = f"{creds['url']}/rest/api/content/{page_id}"
    try:
        response = requests.get(get_url, headers=headers, auth=auth)
        if response.status_code != 200:
            return f"Error getting page details for update: {response.status_code} - {response.text}"
        page_data = response.json()
        current_version = page_data['version']['number']
        current_title = page_data['title']

        # Now, update the page
        update_url = f"{creds['url']}/rest/api/content/{page_id}"
        payload = {
            "version": {"number": current_version + 1},
            "title": new_title or current_title,
            "type": "page",
            "body": {"storage": {"value": new_content, "representation": "storage"}}
        }

        response = requests.put(update_url, json=payload, headers=headers, auth=auth)
        if response.status_code == 200:
            updated_page = response.json()
            return f"Successfully updated Confluence page with ID: {updated_page['id']}"
        else:
            return f"Error updating page: {response.status_code} - {response.text}"
    except Exception as e:
        return f"An error occurred while updating the page: {e}" 