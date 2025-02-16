import pytest
from fastapi.testclient import TestClient
from app.main import app, get_location, get_weather
from fastapi import HTTPException
import pytest_asyncio

client = TestClient(app)

# Basic page tests
def test_home_page():
    """Test if home page loads correctly"""
    response = client.get("/")
    assert response.status_code == 200
    assert "weather dashboard" in response.text.lower()  # Changed from Chinese to English
    # Check necessary DOM elements
    assert 'id="current-temp"' in response.text
    assert 'id="weather-desc"' in response.text
    assert 'id="temp-chart"' in response.text

# API endpoint tests
@pytest.mark.parametrize("city,expected_status,expected_response", [
    # 有效城市测试
    ("London", 200, {"has_main": True, "has_weather": True}),
    ("Beijing", 200, {"has_main": True, "has_weather": True}),
    
    # 无效城市测试 - 应该返回 404 而不是 500
    ("InvalidCityName123456", 404, {"detail": "City not found"}),
    
    # 空城市名测试
    ("", 404, {"detail": "Not Found"}),
])
def test_weather_api_endpoints(city, expected_status, expected_response):
    """Test weather API responses for different inputs"""
    response = client.get(f"/api/weather/{city}")
    assert response.status_code == expected_status
    
    data = response.json()
    
    # 验证成功响应
    if expected_status == 200:
        assert "main" in data, "Response should contain 'main' data"
        assert "weather" in data, "Response should contain 'weather' data"
    else:
        # 验证错误响应
        assert "detail" in data, "Error response should contain 'detail' field"
        if expected_status == 404:
            if city == "":
                assert data["detail"] == "Not Found", \
                    "Empty city should return 'Not Found'"
            else:
                assert data["detail"] == "City not found", \
                    "Invalid city should return 'City not found'"

def test_weather_api_response_structure():
    """测试天气 API 返回的数据结构"""
    response = client.get("/api/weather/London")
    assert response.status_code == 200
    data = response.json()
    
    # 验证返回的数据结构
    required_fields = {
        "main": ["temp", "feels_like", "temp_min", "temp_max", "pressure", "humidity"],
        "weather": ["id", "main", "description", "icon"],
        "wind": ["speed", "deg"],
        "sys": ["sunrise", "sunset"]
    }
    
    for category, fields in required_fields.items():
        assert category in data
        for field in fields:
            if category == "weather":
                assert field in data[category][0]
            else:
                assert field in data[category]

# 位置服务测试
@pytest.mark.asyncio
async def test_get_location_valid_city():
    """测试有效城市的位置获取"""
    location_data = await get_location("London")
    assert location_data is not None
    
    # 转换为字典以便访问
    if hasattr(location_data, 'dict'):
        location = location_data.dict()
    else:
        location = location_data
        
    # 验证必要的字段
    required_fields = ["lat", "lon", "name", "country"]
    for field in required_fields:
        assert field in location, f"Missing field: {field}"
        
    # 验证数据类型
    assert isinstance(location["lat"], (int, float)), "Latitude should be numeric"
    assert isinstance(location["lon"], (int, float)), "Longitude should be numeric"
    assert isinstance(location["name"], str), "Name should be string"
    assert isinstance(location["country"], str), "Country should be string"
    
    # 验证数据有效性
    assert -90 <= location["lat"] <= 90, "Invalid latitude value"
    assert -180 <= location["lon"] <= 180, "Invalid longitude value"
    assert len(location["name"]) > 0, "Name should not be empty"
    assert len(location["country"]) > 0, "Country should not be empty"

@pytest.mark.asyncio
async def test_get_location_invalid_city():
    """测试无效城市的错误处理"""
    location = await get_location("InvalidCityName123456")
    assert location is None, "Invalid city should return None"

# 天气数据测试
@pytest.mark.asyncio
async def test_get_weather_valid_coordinates():
    """测试有效坐标的天气数据获取"""
    weather_data = await get_weather(51.5074, -0.1278)  # London coordinates
    assert weather_data is not None
    assert "main" in weather_data
    assert "weather" in weather_data
    assert len(weather_data["weather"]) > 0

@pytest.mark.asyncio
async def test_get_weather_invalid_coordinates():
    """测试无效坐标的错误处理"""
    with pytest.raises(HTTPException) as exc_info:
        await get_weather(1000, 1000)  # Invalid coordinates
    assert exc_info.value.status_code == 500

# 数据转换测试
def kelvin_to_celsius(kelvin: float) -> float:
    """将开尔文温度转换为摄氏度"""
    return kelvin - 273.15

def test_temperature_conversion():
    """测试温度转换功能"""
    response = client.get("/api/weather/London")
    data = response.json()
    
    # 验证开尔文温度值在合理范围内
    temp_kelvin = data["main"]["temp"]
    assert isinstance(temp_kelvin, (int, float))
    assert 200 < temp_kelvin < 330  # 开尔文温度的合理范围
    
    # 验证转换后的摄氏度在合理范围内
    temp_celsius = kelvin_to_celsius(temp_kelvin)
    assert -60 < temp_celsius < 60  # 摄氏度的合理范围
    
    # 验证其他温度字段
    assert kelvin_to_celsius(data["main"]["feels_like"]) > -60
    assert kelvin_to_celsius(data["main"]["temp_min"]) > -60
    assert kelvin_to_celsius(data["main"]["temp_max"]) < 60

# 错误处理测试
def test_api_error_handling():
    """测试 API 错误处理"""
    # 测试无效的 API 路径
    response = client.get("/api/invalid_endpoint")
    assert response.status_code == 404
    
    # 测试无效的请求方法
    response = client.post("/api/weather/London")
    assert response.status_code == 405

# 性能测试
@pytest.mark.slow
def test_api_response_time():
    """测试 API 响应时间"""
    import time
    start_time = time.time()
    response = client.get("/api/weather/London")
    end_time = time.time()
    
    assert response.status_code == 200
    response_time = end_time - start_time
    
    # 记录响应时间
    print(f"\nAPI Response Time: {response_time:.2f} seconds")
    
    # 调整为更合理的超时时间（5秒）
    assert response_time < 5  # 考虑到网络延迟和外部 API 调用的时间

# 可以添加更细致的性能测试
@pytest.mark.slow
def test_api_performance():
    """详细的性能测试"""
    import time
    import statistics
    
    response_times = []
    test_cities = ["London", "Paris", "Tokyo"]  # 测试多个城市
    
    for city in test_cities:
        start_time = time.time()
        response = client.get(f"/api/weather/{city}")
        end_time = time.time()
        
        assert response.status_code == 200
        response_times.append(end_time - start_time)
    
    # 计算统计数据
    avg_time = statistics.mean(response_times)
    max_time = max(response_times)
    min_time = min(response_times)
    
    print(f"\nPerformance Statistics:")
    print(f"Average Response Time: {avg_time:.2f} seconds")
    print(f"Maximum Response Time: {max_time:.2f} seconds")
    print(f"Minimum Response Time: {min_time:.2f} seconds")
    
    # 性能断言
    assert avg_time < 5  # 平均响应时间应小于5秒
    assert max_time < 7  # 最大响应时间应小于7秒

# 并发测试
@pytest.mark.asyncio
async def test_concurrent_requests():
    """测试并发请求处理"""
    import asyncio
    cities = ["London", "Paris", "Tokyo", "Beijing", "New York"]
    
    async def fetch_weather(city):
        response = client.get(f"/api/weather/{city}")
        return response.status_code
    
    results = await asyncio.gather(*[fetch_weather(city) for city in cities])
    assert all(status == 200 for status in results)

if __name__ == "__main__":
    pytest.main(["-v"])

# 