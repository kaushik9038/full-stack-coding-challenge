"""Fake weather tool.

This does not call a real weather API. It returns pretend weather so the app can
be built and tested without API keys.
"""

import re


WEATHER_BY_CITY = {
    "calgary": "Calgary: 10 C, Sunny",
    "edmonton": "Edmonton: 8 C, Windy",
    "london": "London: 14 C, Cloudy",
    "new york": "New York: 19 C, Sunny",
    "tokyo": "Tokyo: 22 C, Rain showers",
}


def looks_like_weather(lower_task: str) -> bool:
    return "weather" in lower_task or "forecast" in lower_task or "temperature" in lower_task


def get_weather_answer(task_text: str) -> str:
    city = find_city(task_text)
    return WEATHER_BY_CITY.get(city.lower(), f"{city}: 20 C, Clear")


def find_city(task_text: str) -> str:
    match = re.search(r"(?:weather|forecast|temperature)(?:\s+(?:in|for))?\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)?)", task_text, re.IGNORECASE)
    if match:
        city = match.group(1).strip(" ?.!").lower()
        city = re.split(r"\b(?:and|then|plus)\b", city)[0].strip()
        if city:
            return city.title()

    return "Unknown"
