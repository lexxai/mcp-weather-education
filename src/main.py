from fastapi import FastAPI
# from pydantic import BaseModel

from weather import get_alerts_us as _get_alerts_us, get_forecast_us as _get_forecast_us, get_forecast_international as _get_forecast_international

app = FastAPI(title="OpenAI-Compatible API")

@app.get("/get_alerts_us", operation_id="get_alerts_us")
async def get_alerts_us(state: str|None = None) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    if not state:
        return "Please provide a state code (e.g., CA, NY)."
    return await _get_alerts_us(state)


@app.get("/get_forecast_us", operation_id="get_forecast_us")
async def get_forecast_us(latitude: float | None = None, longitude: float | None = None) -> str:
    """Get weather forecast for a location in US.

    Args:
        latitude: Latitude of the location (-90 to 90)
        longitude: Longitude of the location (-180 to 180)
    """
    if not latitude or not longitude:
        return "Please provide latitude and longitude."
    return await _get_forecast_us(latitude, longitude)



@app.get("/get_forecast_international", operation_id="get_forecast_international")
async def get_forecast_international(latitude: float | None = None, longitude: float | None = None) -> str:
    """Get weather forecast for any international location.

    Args:
        latitude: Latitude of the location (-90 to 90)
        longitude: Longitude of the location (-180 to 180)
    """
    if not latitude or not longitude:
        return "Please provide latitude and longitude."
    return await _get_forecast_international(latitude,longitude)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
