"""Weather API endpoints module"""
from fastapi import APIRouter, HTTPException
from ..services.weather import WeatherService

router = APIRouter(prefix="/api/weather")

@router.get("/{city}")
async def get_weather(city: str):
    """Get current weather data for a city
    
    Args:
        city (str): Name of the city to get weather data for
        
    Returns:
        dict: Weather data including temperature, humidity, wind, etc.
        
    Raises:
        HTTPException: If city is not found or other errors occur
    """
    if not city:
        raise HTTPException(status_code=404, detail="Not Found")
        
    try:
        service = WeatherService()
        data = await service.get_weather(city)
        if not data:
            raise HTTPException(
                status_code=500,
                detail="Internal server error: City not found"
            )
        return data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/monthly/{city}")
async def get_monthly_weather(city: str):
    """Get 7-day weather forecast for a city"""
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
        
    try:
        service = WeatherService()
        
        # 第一步：获取城市的地理坐标
        location = await service.get_location(city)
        if not location:
            raise HTTPException(
                status_code=404,
                detail=f"City '{city}' not found"
            )
            
        print(f"Location found: {location}")  # 添加调试日志
            
        # 第二步：使用坐标获取天气预报
        forecast = await service.get_monthly_forecast(location["lat"], location["lon"])
        if not forecast:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch forecast data"
            )
            
        return forecast
        
    except Exception as e:
        print(f"Error in forecast API: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        ) 