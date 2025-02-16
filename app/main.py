"""
天气仪表盘应用主模块

这个模块提供了一个基于 FastAPI 的天气仪表盘应用，包含以下主要功能：
- 天气数据获取和展示
- 城市搜索
- 实时天气信息更新

主要组件：
- WeatherDescription: 天气描述数据模型
- MainWeatherData: 主要天气数据模型
- WindData: 风力数据模型
- LocationData: 位置数据模型
- WeatherData: 完整天气数据模型

使用方法：
    >>> from app.main import app
    >>> uvicorn.run(app, host="127.0.0.1", port=8000)
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pathlib import Path
import httpx
import os
import logging
from dotenv import load_dotenv
from typing import Dict, Any, Optional, TypedDict, List, Union, cast
from pydantic import BaseModel
from .api.weather import router as weather_router
from .services.weather import LocationResult, WeatherService
from .api.htmx import router as htmx_router

# 定义 Pydantic 模型来替代 TypedDict
class WeatherDescription(BaseModel):
    """
    天气描述数据模型

    属性:
        id (int): 天气状况ID
        main (str): 主要天气状况
        description (str): 详细天气描述
        icon (str): 天气图标代码
    """
    id: int
    main: str
    description: str
    icon: str

class MainWeatherData(BaseModel):
    """
    主要天气数据模型

    属性:
        temp (float): 当前温度（开尔文）
        feels_like (float): 体感温度（开尔文）
        temp_min (float): 最低温度（开尔文）
        temp_max (float): 最高温度（开尔文）
        pressure (int): 大气压力（百帕）
        humidity (int): 相对湿度（百分比）
        sea_level (Optional[int]): 海平面气压（百帕）
        grnd_level (Optional[int]): 地面气压（百帕）
    """
    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    pressure: int
    humidity: int
    sea_level: Optional[int] = None
    grnd_level: Optional[int] = None

class WindData(BaseModel):
    """
    风力数据模型

    属性:
        speed (float): 风速（米/秒）
        deg (int): 风向（度）
        gust (Optional[float]): 阵风速度（米/秒）
    """
    speed: float
    deg: int
    gust: Optional[float] = None

class LocationData(BaseModel):
    """
    位置数据模型

    属性:
        lat (float): 纬度
        lon (float): 经度
        name (str): 城市名称
        country (str): 国家代码
    """
    lat: float
    lon: float
    name: str
    country: str
    class Config:
        extra = "allow"  # 允许额外字段

class WeatherData(BaseModel):
    """
    完整天气数据模型

    属性:
        coord (Dict[str, float]): 坐标信息
        weather (List[WeatherDescription]): 天气状况列表
        base (str): 数据源
        main (MainWeatherData): 主要天气数据
        visibility (int): 能见度（米）
        wind (WindData): 风力数据
        clouds (Dict[str, int]): 云量数据
        rain (Optional[Dict[str, float]]): 降水量数据
        dt (int): 数据更新时间戳
        sys (Dict[str, Any]): 系统相关数据
        timezone (int): 时区偏移（秒）
        id (int): 城市ID
        name (str): 城市名称
        cod (int): API响应状态码
        location (Optional[LocationData]): 位置详细信息
    """
    coord: Dict[str, float]
    weather: List[WeatherDescription]
    base: str
    main: MainWeatherData
    visibility: int
    wind: WindData
    clouds: Dict[str, int]
    rain: Optional[Dict[str, float]] = None
    dt: int
    sys: Dict[str, Any]
    timezone: int
    id: int
    name: str
    cod: int
    location: Optional[Dict[str, Any]] = None  # 使其可选且更灵活
    class Config:
        extra = "allow"  # 允许额外字段

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger: logging.Logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

app = FastAPI(title="天气仪表盘")

# 设置静态文件和模板
BASE_DIR: Path = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# API配置
API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")
if not API_KEY:
    raise ValueError("Missing OPENWEATHER_API_KEY in .env file")

logger.debug(f"Using API key: {API_KEY[:4]}...")  # 只显示前4位

GEO_API_URL: str = "http://api.openweathermap.org/geo/1.0/direct"
WEATHER_API_URL: str = "https://api.openweathermap.org/data/2.5/weather"

async def get_location(city: str) -> Optional[LocationData]:
    """获取城市位置信息"""
    try:
        service = WeatherService()
        location_data = await service.get_location(city)
        if location_data:
            # 使用 Pydantic 模型创建实例
            return LocationData(**location_data)
        return None
    except Exception as e:
        logger.error(f"Error getting location: {e}")
        return None

async def get_weather(lat: float, lon: float) -> WeatherData:
    """
    根据经纬度获取天气数据

    Args:
        lat (float): 纬度
        lon (float): 经度

    Returns:
        WeatherData: 包含完整天气信息的数据对象

    Raises:
        HTTPException: 当API请求失败时抛出
    """
    try:
        logger.debug(f"Fetching weather for coordinates: lat={lat}, lon={lon}")
        async with httpx.AsyncClient(timeout=10.0) as client:
            params: Dict[str, Union[str, float]] = {
                "lat": lat,
                "lon": lon,
                "appid": API_KEY,
                "lang": "zh_cn"
            }
            response = await client.get(WEATHER_API_URL, params=params)
            logger.debug(f"Weather API response status: {response.status_code}")
            
            response.raise_for_status()
            data: WeatherData = response.json()
            logger.debug(f"Weather API response data: {data}")
            return data
    except httpx.TimeoutException as e:
        logger.error(f"Timeout error: {e}")
        raise HTTPException(status_code=504, detail="Request timeout")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    """
    渲染主页面

    Args:
        request (Request): FastAPI请求对象

    Returns:
        HTMLResponse: 渲染后的HTML响应
    """
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )

@app.get("/api/weather/{city}", response_model=WeatherData)
async def get_city_weather(city: str):
    try:
        if not city:
            raise HTTPException(status_code=422, detail="City name cannot be empty")
            
        # 1. 获取城市经纬度
        location_data = await get_location(city)
        if not location_data:
            raise HTTPException(status_code=404, detail="City not found")
        
        # 2. 获取天气数据
        location_dict = location_data.dict()  # 转换为字典
        weather_data = await get_weather(location_dict["lat"], location_dict["lon"])
        
        # 3. 添加位置信息
        weather_dict = dict(weather_data)
        weather_dict["location"] = location_dict
        
        return WeatherData(**weather_dict)
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in get_city_weather: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get('/favicon.ico', include_in_schema=False)
async def favicon() -> FileResponse:
    """返回网站图标"""
    return FileResponse(
        os.path.join(BASE_DIR, 'static', 'favicon.ico'),
        media_type='image/x-icon'
    )

@app.get("/monthly", response_class=HTMLResponse)
async def monthly_dashboard(request: Request) -> HTMLResponse:
    """Render monthly forecast dashboard"""
    return templates.TemplateResponse(
        "monthly_dashboard.html",
        {"request": request}
    )

# Register API routes
app.include_router(weather_router)
app.include_router(htmx_router) 