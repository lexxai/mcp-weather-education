from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

from pydantic import BaseModel, Field

from weather import (
    get_alerts_us as _get_alerts_us,
    get_forecast_us as _get_forecast_us,
    get_forecast_international as _get_forecast_international,
)

app = FastAPI(title="MCP OpenAPI-Compatible API server for weather")


class Coordinates(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="Latitude of the location")
    longitude: float = Field(
        ..., ge=-180, le=180, description="Longitude of the location"
    )


@app.get(
    "/get_alerts_us",
    operation_id="get_alerts_us",
    summary="Get US Alerts",
    description="Returns weather alerts for a US state. Requires a two-letter state code.",
)
async def get_alerts_us(state: str | None = None) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    if not state:
        return "Please provide a state code (e.g., CA, NY)."
    return await _get_alerts_us(state)


@app.post(
    "/get_forecast_us",
    operation_id="get_forecast_us",
    summary="Get US forecast",
)
async def get_forecast_us(req: Coordinates) -> str:
    """Get weather forecast for a location in US.

    Args:
        latitude: Latitude of the location (-90 to 90)
        longitude: Longitude of the location (-180 to 180)
    """
    return await _get_forecast_us(req.latitude, req.longitude)


@app.post("/get_forecast_international", operation_id="get_forecast_international")
async def get_forecast_international(req: Coordinates) -> str:
    """Get weather forecast for any international location.

    Args:
        latitude: Latitude of the location (-90 to 90)
        longitude: Longitude of the location (-180 to 180)
    """
    return await _get_forecast_international(req.latitude, req.longitude)


mcp = FastApiMCP(app, name="MCP [see] server for weather")

mcp.mount_http()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
