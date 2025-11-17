import logging
import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
port = os.environ.get("APP_PORT", 8000)
mcp = FastMCP("weather", host="0.0.0.0", port=port)

# Constants
NWS_API_BASE = "https://api.weather.gov"
INTERNATIONAL_API_BASE = "https://api.open-meteo.com"
USER_AGENT = "weather-app/1.0"
REQUEST_TIMEOUT = 30.0


async def make_http_request(url: str) -> dict[str, Any] | None:
    """Make a request to the API with proper error handling.

    Args:
        url: The URL to request

    Returns:
        JSON response as dict, or None if request failed
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for URL: {url}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error for URL {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error for URL {url}: {e}")
            return None


def format_alert(feature: dict[str, Any]) -> str:
    """Format an alert feature into a readable string.

    Args:
        feature: Alert feature from NWS API

    Returns:
        Formatted alert string
    """
    props = feature.get("properties", {})
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
        return "Unable to fetch forecast data for this location. Ensure coordinates are within the US."

    # Get the forecast URL from the points response
    try:
        forecast_url = points_data["properties"]["forecast"]
    except KeyError:
        logger.error(f"Missing 'forecast' in points response for {latitude},{longitude}")
        return "Invalid response format from weather service."

    forecast_data = await make_http_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # Format the periods into a readable forecast
    try:
        periods = forecast_data["properties"]["periods"]
    except KeyError:
        logger.error("Missing 'periods' in forecast response")
        return "Invalid forecast data format."

    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
{period.get('name', 'Unknown')}:
Temperature: {period.get('temperature', 'N/A')}°{period.get('temperatureUnit', 'F')}
Wind: {period.get('windSpeed', 'N/A')} {period.get('windDirection', '')}
Forecast: {period.get('detailedForecast', 'No forecast available')}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)


@mcp.tool()
async def get_forecast_international(latitude: float, longitude: float) -> str:
    """Get weather forecast for any international location.

    Args:
        latitude: Latitude of the location (-90 to 90)
        longitude: Longitude of the location (-180 to 180)
    """
    # Validate coordinates
    if not (-90 <= latitude <= 90):
        return f"Invalid latitude: {latitude}. Must be between -90 and 90."
    if not (-180 <= longitude <= 180):
        return f"Invalid longitude: {longitude}. Must be between -180 and 180."

    # Open-Meteo is free and doesn't require API key
    url = (f"{INTERNATIONAL_API_BASE}/v1/forecast?latitude={latitude}&longitude={longitude}"
           "&current=temperature_2m,weather_code,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min,weather_code"
           "&timezone=auto")

    data = await make_http_request(url)

    if not data:
        return "Unable to fetch international forecast data."

    try:
        # Format current weather
        current = data['current']
        forecasts = [f"""
Current Weather:
Temperature: {current.get('temperature_2m', 'N/A')}°C
Wind Speed: {current.get('wind_speed_10m', 'N/A')} km/h
"""]

        # Format daily forecast
        daily = data['daily']
        for i in range(min(5, len(daily.get('time', [])))):
            forecast = f"""
{daily['time'][i]}:
High: {daily['temperature_2m_max'][i]}°C
Low: {daily['temperature_2m_min'][i]}°C
Weather Code: {daily['weather_code'][i]}
"""
            forecasts.append(forecast)

        return "\n---\n".join(forecasts)
    except (KeyError, IndexError) as e:
        logger.error(f"Error parsing international forecast data: {e}")
        return "Invalid forecast data format received."


def main() -> None:
    """Run the MCP server with stdio transport."""
    logger.info("Starting weather MCP server with stdio transport")
    mcp.run(transport='stdio')


def main_http() -> None:
    """Run the MCP server with HTTP transport."""
    logger.info("Starting weather MCP server with HTTP transport")
    mcp.run(transport='streamable-http')


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "http":
        main_http()
    else:
        main()
