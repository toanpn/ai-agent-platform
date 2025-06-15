"""
Google Calendar tool functions for managing calendar events.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from .common.http_client import create_authenticated_client
from .registry import get_tool_registry

logger = logging.getLogger(__name__)


def create_google_calendar_event(
    google_api_key: str,
    calendar_id: str = "primary",
    summary: str = None,
    description: str = None,
    start_time: str = None,
    end_time: str = None,
    location: str = None,
    attendees: List[str] = None,
    reminder_minutes: int = 10,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a new Google Calendar event.
    
    Args:
        google_api_key: Google API key
        calendar_id: Calendar ID (default: "primary")
        summary: Event summary/title
        description: Event description
        start_time: Event start time (ISO format: 2023-12-01T10:00:00Z)
        end_time: Event end time (ISO format: 2023-12-01T11:00:00Z)
        location: Event location
        attendees: List of attendee email addresses
        reminder_minutes: Reminder time in minutes (default: 10)
        **kwargs: Additional parameters
        
    Returns:
        Dict[str, Any]: Created event information
        
    Raises:
        Exception: If event creation fails
    """
    logger.info(f"Creating Google Calendar event: {summary}")
    
    try:
        # Create authenticated client using API key
        client = create_authenticated_client(
            base_url="https://www.googleapis.com/calendar/v3",
            auth_type="api_key",
            api_key=google_api_key,
            api_key_header="key"
        )
        
        # Prepare event data
        event_data = {
            "summary": summary,
            "description": description,
            "start": {
                "dateTime": start_time,
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": end_time,
                "timeZone": "UTC"
            }
        }
        
        # Add location if provided
        if location:
            event_data["location"] = location
        
        # Add attendees if provided
        if attendees:
            event_data["attendees"] = [{"email": email} for email in attendees]
        
        # Add reminder
        if reminder_minutes:
            event_data["reminders"] = {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": reminder_minutes},
                    {"method": "popup", "minutes": reminder_minutes}
                ]
            }
        
        # Create the event
        response = client.post(
            f"/calendars/{calendar_id}/events",
            json_data=event_data,
            headers={"Content-Type": "application/json"}
        )
        
        result = {
            "success": True,
            "event_id": response.get("id"),
            "summary": response.get("summary"),
            "start_time": response.get("start", {}).get("dateTime"),
            "end_time": response.get("end", {}).get("dateTime"),
            "location": response.get("location"),
            "html_link": response.get("htmlLink"),
            "status": response.get("status"),
            "created": response.get("created"),
            "updated": response.get("updated")
        }
        
        logger.info(f"Successfully created Google Calendar event: {response.get('id')}")
        return result
        
    except Exception as e:
        logger.error(f"Error creating Google Calendar event: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to create Google Calendar event: {str(e)}"
        }


def find_free_time(
    google_api_key: str,
    calendar_id: str = "primary",
    start_date: str = None,
    end_date: str = None,
    duration_minutes: int = 60,
    working_hours_start: int = 9,
    working_hours_end: int = 17,
    **kwargs
) -> Dict[str, Any]:
    """
    Find free time slots in Google Calendar.
    
    Args:
        google_api_key: Google API key
        calendar_id: Calendar ID (default: "primary")
        start_date: Search start date (ISO format: 2023-12-01T00:00:00Z)
        end_date: Search end date (ISO format: 2023-12-07T23:59:59Z)
        duration_minutes: Required meeting duration in minutes (default: 60)
        working_hours_start: Working hours start (24-hour format, default: 9)
        working_hours_end: Working hours end (24-hour format, default: 17)
        **kwargs: Additional parameters
        
    Returns:
        Dict[str, Any]: Available free time slots
        
    Raises:
        Exception: If search fails
    """
    logger.info(f"Finding free time slots for {duration_minutes} minutes")
    
    try:
        # Create authenticated client
        client = create_authenticated_client(
            base_url="https://www.googleapis.com/calendar/v3",
            auth_type="api_key",
            api_key=google_api_key,
            api_key_header="key"
        )
        
        # Get busy times using freebusy query
        freebusy_data = {
            "timeMin": start_date,
            "timeMax": end_date,
            "items": [{"id": calendar_id}]
        }
        
        freebusy_response = client.post("/freeBusy", json_data=freebusy_data)
        
        # Extract busy periods
        busy_periods = []
        calendar_data = freebusy_response.get("calendars", {}).get(calendar_id, {})
        for busy_time in calendar_data.get("busy", []):
            busy_periods.append({
                "start": busy_time.get("start"),
                "end": busy_time.get("end")
            })
        
        # Find free slots
        free_slots = _find_free_slots(
            start_date, end_date, busy_periods,
            duration_minutes, working_hours_start, working_hours_end
        )
        
        result = {
            "success": True,
            "duration_minutes": duration_minutes,
            "working_hours": f"{working_hours_start}:00 - {working_hours_end}:00",
            "search_period": f"{start_date} to {end_date}",
            "busy_periods": busy_periods,
            "free_slots": free_slots,
            "total_free_slots": len(free_slots)
        }
        
        logger.info(f"Found {len(free_slots)} free time slots")
        return result
        
    except Exception as e:
        logger.error(f"Error finding free time: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to find free time: {str(e)}"
        }


def get_calendar_events(
    google_api_key: str,
    calendar_id: str = "primary",
    time_min: str = None,
    time_max: str = None,
    max_results: int = 10,
    **kwargs
) -> Dict[str, Any]:
    """
    Get Google Calendar events for a time period.
    
    Args:
        google_api_key: Google API key
        calendar_id: Calendar ID (default: "primary")
        time_min: Start time (ISO format)
        time_max: End time (ISO format)
        max_results: Maximum number of events to return (default: 10)
        **kwargs: Additional parameters
        
    Returns:
        Dict[str, Any]: Calendar events
        
    Raises:
        Exception: If retrieval fails
    """
    logger.info(f"Getting Google Calendar events from {time_min} to {time_max}")
    
    try:
        # Create authenticated client
        client = create_authenticated_client(
            base_url="https://www.googleapis.com/calendar/v3",
            auth_type="api_key",
            api_key=google_api_key,
            api_key_header="key"
        )
        
        # Prepare query parameters
        params = {
            "maxResults": max_results,
            "singleEvents": True,
            "orderBy": "startTime"
        }
        
        if time_min:
            params["timeMin"] = time_min
        if time_max:
            params["timeMax"] = time_max
        
        # Get events
        response = client.get(f"/calendars/{calendar_id}/events", params=params)
        
        events = []
        for event in response.get("items", []):
            events.append({
                "event_id": event.get("id"),
                "summary": event.get("summary"),
                "description": event.get("description"),
                "start_time": event.get("start", {}).get("dateTime") or event.get("start", {}).get("date"),
                "end_time": event.get("end", {}).get("dateTime") or event.get("end", {}).get("date"),
                "location": event.get("location"),
                "status": event.get("status"),
                "html_link": event.get("htmlLink"),
                "created": event.get("created"),
                "updated": event.get("updated")
            })
        
        result = {
            "success": True,
            "events": events,
            "total_events": len(events),
            "calendar_id": calendar_id,
            "time_range": f"{time_min} to {time_max}"
        }
        
        logger.info(f"Retrieved {len(events)} calendar events")
        return result
        
    except Exception as e:
        logger.error(f"Error getting calendar events: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get calendar events: {str(e)}"
        }


def _find_free_slots(
    start_date: str,
    end_date: str,
    busy_periods: List[Dict[str, str]],
    duration_minutes: int,
    working_hours_start: int,
    working_hours_end: int
) -> List[Dict[str, str]]:
    """
    Find free time slots between busy periods.
    
    Args:
        start_date: Search start date
        end_date: Search end date
        busy_periods: List of busy time periods
        duration_minutes: Required slot duration
        working_hours_start: Working hours start
        working_hours_end: Working hours end
        
    Returns:
        List[Dict[str, str]]: Free time slots
    """
    from datetime import datetime, timedelta
    import dateutil.parser
    
    try:
        # Parse dates
        start_dt = dateutil.parser.parse(start_date)
        end_dt = dateutil.parser.parse(end_date)
        duration = timedelta(minutes=duration_minutes)
        
        # Convert busy periods to datetime objects
        busy_times = []
        for period in busy_periods:
            busy_start = dateutil.parser.parse(period["start"])
            busy_end = dateutil.parser.parse(period["end"])
            busy_times.append((busy_start, busy_end))
        
        # Sort busy times
        busy_times.sort(key=lambda x: x[0])
        
        free_slots = []
        current_time = start_dt
        
        # Iterate through days
        while current_time.date() <= end_dt.date():
            # Set working hours for current day
            day_start = current_time.replace(hour=working_hours_start, minute=0, second=0, microsecond=0)
            day_end = current_time.replace(hour=working_hours_end, minute=0, second=0, microsecond=0)
            
            # Find free slots in this day
            slot_start = day_start
            
            for busy_start, busy_end in busy_times:
                # Skip if busy period is not in current day
                if busy_start.date() != current_time.date():
                    continue
                
                # If there's a gap before the busy period
                if slot_start + duration <= busy_start and slot_start >= day_start:
                    # Find all possible slots in this gap
                    while slot_start + duration <= min(busy_start, day_end):
                        free_slots.append({
                            "start": slot_start.isoformat(),
                            "end": (slot_start + duration).isoformat(),
                            "duration_minutes": duration_minutes
                        })
                        slot_start += timedelta(minutes=30)  # 30-minute intervals
                
                # Move to after the busy period
                slot_start = max(slot_start, busy_end)
            
            # Check for slots after the last busy period
            while slot_start + duration <= day_end:
                free_slots.append({
                    "start": slot_start.isoformat(),
                    "end": (slot_start + duration).isoformat(),
                    "duration_minutes": duration_minutes
                })
                slot_start += timedelta(minutes=30)
            
            # Move to next day
            current_time += timedelta(days=1)
        
        return free_slots[:20]  # Limit to 20 slots
        
    except Exception as e:
        logger.error(f"Error finding free slots: {e}")
        return []


# Register tools in the registry
def _register_google_calendar_tools():
    """Register Google Calendar tools in the tool registry."""
    registry = get_tool_registry()
    
    # Create calendar event tool
    registry.register_tool(
        name="create_google_calendar_event",
        function=create_google_calendar_event,
        description="Create a new Google Calendar event",
        required_credentials=["google_api_key"],
        parameters_schema={
            "type": "object",
            "properties": {
                "calendar_id": {"type": "string", "description": "Calendar ID", "default": "primary"},
                "summary": {"type": "string", "description": "Event summary/title"},
                "description": {"type": "string", "description": "Event description"},
                "start_time": {"type": "string", "description": "Start time (ISO format)"},
                "end_time": {"type": "string", "description": "End time (ISO format)"},
                "location": {"type": "string", "description": "Event location"},
                "attendees": {"type": "array", "items": {"type": "string"}, "description": "Attendee emails"},
                "reminder_minutes": {"type": "integer", "description": "Reminder minutes", "default": 10}
            },
            "required": ["summary", "start_time", "end_time"]
        },
        category="calendar"
    )
    
    # Find free time tool
    registry.register_tool(
        name="find_free_time",
        function=find_free_time,
        description="Find free time slots in Google Calendar",
        required_credentials=["google_api_key"],
        parameters_schema={
            "type": "object",
            "properties": {
                "calendar_id": {"type": "string", "description": "Calendar ID", "default": "primary"},
                "start_date": {"type": "string", "description": "Search start date (ISO format)"},
                "end_date": {"type": "string", "description": "Search end date (ISO format)"},
                "duration_minutes": {"type": "integer", "description": "Meeting duration", "default": 60},
                "working_hours_start": {"type": "integer", "description": "Working hours start", "default": 9},
                "working_hours_end": {"type": "integer", "description": "Working hours end", "default": 17}
            },
            "required": ["start_date", "end_date"]
        },
        category="calendar"
    )
    
    # Get calendar events tool
    registry.register_tool(
        name="get_calendar_events",
        function=get_calendar_events,
        description="Get Google Calendar events for a time period",
        required_credentials=["google_api_key"],
        parameters_schema={
            "type": "object",
            "properties": {
                "calendar_id": {"type": "string", "description": "Calendar ID", "default": "primary"},
                "time_min": {"type": "string", "description": "Start time (ISO format)"},
                "time_max": {"type": "string", "description": "End time (ISO format)"},
                "max_results": {"type": "integer", "description": "Maximum results", "default": 10}
            },
            "required": ["time_min", "time_max"]
        },
        category="calendar"
    )


# Register tools when module is imported
_register_google_calendar_tools() 