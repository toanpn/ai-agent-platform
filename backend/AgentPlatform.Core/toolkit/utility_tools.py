import os
import requests
from datetime import datetime, timedelta
from langchain.tools import tool
from typing import Optional

@tool
def google_search(query: str) -> str:
    """
    Performs a Google search and returns the top results.
    Use this tool when you need to search for current information on the internet.
    
    Args:
        query: The search query string
    """
    try:
        # For demonstration, we'll use a simplified search
        # In production, you would use Google Custom Search API or similar
        api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        
        if api_key and search_engine_id:
            # Real Google Search API implementation
            url = f"https://www.googleapis.com/customsearch/v1"
            params = {
                'key': api_key,
                'cx': search_engine_id,
                'q': query,
                'num': 5
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get('items', []):
                    title = item.get('title', '')
                    snippet = item.get('snippet', '')
                    link = item.get('link', '')
                    results.append(f"• {title}\n  {snippet}\n  🔗 {link}")
                
                if results:
                    return f"🔍 Search results for '{query}':\n\n" + "\n\n".join(results)
                else:
                    return f"No search results found for '{query}'"
            else:
                return f"Search API error: {response.status_code}"
        else:
            # Mock search results for demonstration
            mock_results = [
                {
                    "title": f"Latest information about {query}",
                    "snippet": f"Comprehensive guide and recent updates about {query}. This covers the most important aspects and current trends.",
                    "url": "https://example.com/search-1"
                },
                {
                    "title": f"How to {query} - Complete Guide",
                    "snippet": f"Step-by-step instructions and best practices for {query}. Learn from experts and get practical tips.",
                    "url": "https://example.com/guide-2"
                },
                {
                    "title": f"{query} - News and Updates",
                    "snippet": f"Recent news and developments related to {query}. Stay informed with the latest information.",
                    "url": "https://example.com/news-3"
                }
            ]
            
            formatted_results = []
            for result in mock_results:
                formatted_results.append(f"• {result['title']}\n  {result['snippet']}\n  🔗 {result['url']}")
            
            return f"🔍 Search results for '{query}':\n\n" + "\n\n".join(formatted_results)
            
    except Exception as e:
        return f"Error performing Google search: {str(e)}"

@tool
def check_calendar(date: str = "") -> str:
    """
    Checks calendar events for a specified date or today.
    Use this tool when users want to know about upcoming meetings or events.
    
    Args:
        date: Date to check in YYYY-MM-DD format. If empty, checks today.
    """
    try:
        # Parse the date or use today
        if not date:
            target_date = datetime.now()
            date_str = target_date.strftime("%Y-%m-%d")
        else:
            target_date = datetime.strptime(date, "%Y-%m-%d")
            date_str = date
        
        # Mock calendar data - in production, integrate with Google Calendar API, Outlook, etc.
        mock_events = {
            datetime.now().strftime("%Y-%m-%d"): [
                {"time": "09:00", "title": "Team Standup", "duration": "30 min", "location": "Conference Room A"},
                {"time": "14:00", "title": "Project Review Meeting", "duration": "1 hour", "location": "Zoom"},
                {"time": "16:30", "title": "Client Call", "duration": "45 min", "location": "Phone"}
            ],
            (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"): [
                {"time": "10:00", "title": "All Hands Meeting", "duration": "1 hour", "location": "Main Auditorium"},
                {"time": "15:00", "title": "Code Review", "duration": "30 min", "location": "Dev Room"}
            ]
        }
        
        events = mock_events.get(date_str, [])
        
        if events:
            event_list = []
            for event in events:
                event_list.append(f"🕐 {event['time']} - {event['title']}")
                event_list.append(f"   Duration: {event['duration']}")
                event_list.append(f"   Location: {event['location']}")
                event_list.append("")  # Empty line for spacing
            
            return f"📅 Calendar for {target_date.strftime('%A, %B %d, %Y')}:\n\n" + "\n".join(event_list)
        else:
            return f"📅 No events scheduled for {target_date.strftime('%A, %B %d, %Y')}. Your calendar is free!"
            
    except ValueError:
        return "Invalid date format. Please use YYYY-MM-DD format (e.g., 2024-01-15)"
    except Exception as e:
        return f"Error checking calendar: {str(e)}"

@tool
def check_weather(location: str = "current location") -> str:
    """
    Checks current weather conditions and forecast for a specified location.
    Use this tool when users want to know about weather conditions.
    
    Args:
        location: Location to check weather for (city, country, etc.)
    """
    try:
        # For demonstration, we'll use mock weather data
        # In production, you would use OpenWeatherMap API, Weather.com API, etc.
        api_key = os.getenv("WEATHER_API_KEY")
        
        if api_key:
            # Real weather API implementation (OpenWeatherMap example)
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': location,
                'appid': api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                
                temp = data['main']['temp']
                feels_like = data['main']['feels_like']
                humidity = data['main']['humidity']
                description = data['weather'][0]['description'].title()
                city = data['name']
                country = data['sys']['country']
                
                return f"""🌤️ Weather for {city}, {country}:

Current: {temp}°C (feels like {feels_like}°C)
Condition: {description}
Humidity: {humidity}%

Have a great day! 🌟"""
            else:
                return f"Weather API error for '{location}': {response.status_code}"
        else:
            # Mock weather data for demonstration
            import random
            
            weather_conditions = [
                {"temp": 22, "condition": "Sunny", "humidity": 45, "emoji": "☀️"},
                {"temp": 18, "condition": "Partly Cloudy", "humidity": 60, "emoji": "⛅"},
                {"temp": 15, "condition": "Overcast", "humidity": 75, "emoji": "☁️"},
                {"temp": 12, "condition": "Light Rain", "humidity": 85, "emoji": "🌦️"},
                {"temp": 25, "condition": "Clear Sky", "humidity": 40, "emoji": "🌞"}
            ]
            
            weather = random.choice(weather_conditions)
            
            return f"""{weather['emoji']} Weather for {location}:

Current Temperature: {weather['temp']}°C
Condition: {weather['condition']}
Humidity: {weather['humidity']}%

3-Day Forecast:
• Today: {weather['condition']}, High {weather['temp'] + 2}°C, Low {weather['temp'] - 5}°C
• Tomorrow: Partly Cloudy, High {weather['temp'] + 1}°C, Low {weather['temp'] - 4}°C  
• Day After: Sunny, High {weather['temp'] + 3}°C, Low {weather['temp'] - 3}°C

Have a wonderful day! 🌟"""
            
    except Exception as e:
        return f"Error checking weather: {str(e)}" 