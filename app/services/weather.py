import requests
from datetime import datetime
from typing import Dict, Any, Optional, TypedDict, Union, cast, Mapping
from typing_extensions import TypedDict, NotRequired
import httpx
import os
from requests.models import PreparedRequest

# 定义更灵活的类型
ApiParams = Dict[str, Union[str, int, float, None]]
ApiResponse = Dict[str, Any]
RequestParams = Mapping[str, Union[str, int, float]]

# 定义更详细的类型
class WeatherParams(TypedDict, total=False):
    lat: float
    lon: float
    appid: str
    units: str
    lang: str

class GeoParams(TypedDict, total=False):
    q: str
    limit: int
    appid: str

class LocationResult(TypedDict):
    lat: float
    lon: float
    name: str
    country: str

class WeatherService:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.geo_url = "http://api.openweathermap.org/geo/1.0"

    async def get_weather(self, city: str) -> Optional[ApiResponse]:
        """Get weather data for a city"""
        try:
            # Get city location
            geo_params: ApiParams = {
                "q": city,
                "limit": 1,
                "appid": self.api_key
            }
            
            async with httpx.AsyncClient() as client:
                # Get location info
                geo_response = await client.get(f"{self.geo_url}/direct", params=geo_params)
                geo_response.raise_for_status()
                locations = geo_response.json()
                
                if not locations:
                    return None
                    
                location = locations[0]
                
                # Get weather data with English language setting
                weather_params = {
                    "lat": location["lat"],
                    "lon": location["lon"],
                    "appid": self.api_key,
                    "lang": "en",  # Force English language
                    "units": "standard"
                }
                
                # Make weather API call
                weather_response = await client.get(
                    f"{self.base_url}/weather", 
                    params=weather_params,
                    headers={"Accept-Language": "en"}  # Additional language header
                )
                weather_response.raise_for_status()
                weather_data = weather_response.json()
                
                # Add location info
                weather_data["location"] = {
                    "lat": location["lat"],
                    "lon": location["lon"],
                    "name": location["name"],
                    "country": location["country"]
                }
                
                return weather_data
                
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return None

    def get_weather_by_location(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """获取指定位置的天气数据"""
        url = f"{self.base_url}/onecall"
        params: RequestParams = {
            "lat": lat,
            "lon": lon,
            "appid": str(self.api_key),
            "units": "metric",
            "lang": "en"
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            return {
                "current": {
                    "temp": round(data["current"]["temp"]),
                    "feels_like": round(data["current"]["feels_like"]),
                    "humidity": data["current"]["humidity"],
                    "pressure": data["current"]["pressure"],
                    "wind_speed": round(data["current"]["wind_speed"] * 3.6, 2),  # m/s 转 km/h
                    "wind_deg": data["current"]["wind_deg"],
                    "weather": data["current"]["weather"][0],
                },
                "hourly": data["hourly"][:24],  # 24小时预报
                "daily": data["daily"][:7],     # 7天预报
                "alerts": data.get("alerts", [])
            }
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return None

    def get_weather_by_city(self, city: str) -> Optional[Dict[str, Any]]:
        """通过城市名获取天气数据"""
        geo_url = "http://api.openweathermap.org/geo/1.0/direct"
        params: RequestParams = {
            "q": city,
            "limit": 1,
            "appid": str(self.api_key)
        }

        try:
            response = requests.get(geo_url, params=params)
            response.raise_for_status()
            locations = response.json()
            
            if not locations:
                return None
                
            location = locations[0]
            return self.get_weather_by_location(location["lat"], location["lon"])
        except Exception as e:
            print(f"Error fetching city data: {e}")
            return None

    async def get_location(self, city: str) -> Optional[ApiResponse]:
        """Get location coordinates for a city"""
        try:
            params: ApiParams = {
                "q": city,
                "limit": 5,  # 设置为5，与API示例一致
                "appid": self.api_key
            }
            
            async with httpx.AsyncClient() as client:
                # 使用正确的地理编码API
                response = await client.get(
                    f"{self.geo_url}/direct",
                    params=params,
                    timeout=30.0
                )
                print(f"Geo API Response: {response.text}")  # 添加调试日志
                response.raise_for_status()
                locations = response.json()
                
                if not locations:
                    return None
                    
                location = locations[0]  # 使用第一个结果
                return {
                    "lat": location["lat"],
                    "lon": location["lon"],
                    "name": location["name"],
                    "country": location["country"]
                }
                
        except Exception as e:
            print(f"Error getting location data: {e}")
            return None

    async def get_monthly_forecast(self, lat: float, lon: float) -> Optional[ApiResponse]:
        """Get 7-day weather forecast for a location"""
        try:
            params: ApiParams = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "standard",
                "cnt": 40  # 获取更多数据点以覆盖5天
            }
            
            async with httpx.AsyncClient() as client:
                # 使用免费版的 forecast 接口
                response = await client.get(
                    f"{self.base_url}/forecast",  # 改用 forecast 接口
                    params=params,
                    timeout=30.0
                )
                print(f"Weather API Response: {response.text}")
                response.raise_for_status()
                data = response.json()
                
                # 处理数据，按天聚合
                daily_data = {}
                for item in data['list']:
                    date = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
                    if date not in daily_data:
                        daily_data[date] = {
                            'dt': item['dt'],
                            'temp': {
                                'day': item['main']['temp'],
                                'min': item['main']['temp_min'],
                                'max': item['main']['temp_max']
                            },
                            'humidity': item['main']['humidity'],
                            'weather': item['weather'],
                            'speed': item['wind']['speed'],
                            'rain': item.get('rain', {}).get('3h', 0)
                        }
                
                # 转换为列表格式
                result = {
                    'city': data['city'],
                    'cod': data['cod'],
                    'message': 0,
                    'cnt': len(daily_data),
                    'list': list(daily_data.values())
                }
                
                return result
                
        except Exception as e:
            print(f"Error in forecast API: {e}")
            return None 