from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("weather")

# Constants
NWS_API_BASE = "https://api.weather.gov"
INTERNATIONAL_API_BASE = "https://api.open-meteo.com"
USER_AGENT = "weather-app/1.0"


async def make_http_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""


@mcp.tool()
async def get_alerts_us(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_http_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

@mcp.tool()
async def get_forecast_us(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location in US.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_http_request(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location."

    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_http_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)


@mcp.tool()
async def get_forecast_international(latitude: float, longitude: float) -> str:
    """Get weather forecast for any international location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # Open-Meteo is free and doesn't require API key
    url = (f"https://{INTERNATIONAL_API_BASE}/v1/forecast?latitude={latitude}&longitude={longitude}"
           "&current=temperature_2m,weather_code,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min,weather_code"
           "&timezone=auto")

    data = await make_http_request(url)

    # Format current weather
    current = data['current']
    forecasts = [f"""
Current Weather:
Temperature: {current['temperature_2m']}°C
Wind Speed: {current['wind_speed_10m']} km/h
"""]

    # Format daily forecast
    daily = data['daily']
    for i in range(min(5, len(daily['time']))):
        forecast = f"""
{daily['time'][i]}:
High: {daily['temperature_2m_max'][i]}°C
Low: {daily['temperature_2m_min'][i]}°C
Weather Code: {daily['weather_code'][i]}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)


def main():
    # Initialize and run the server
    mcp.run(transport='stdio')

def main_http():
    # Initialize and run the server
    mcp.run(transport='streamable-http')

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "http":
        main_http()
    else:
        main()
