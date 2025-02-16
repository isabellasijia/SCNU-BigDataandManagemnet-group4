"""HTMX 演示接口"""
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter(prefix="/htmx")

# 设置模板目录
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

@router.get("/demo")
async def htmx_demo(request: Request):
    """HTMX 演示页面"""
    return templates.TemplateResponse(
        "htmx/demo.html",
        {"request": request}
    )

@router.get("/search")
async def htmx_search(request: Request, query: str = ""):
    """HTMX 搜索示例"""
    # 模拟搜索结果
    cities = [
        "London",
        "Paris",
        "New York",
        "Tokyo",
        "Beijing"
    ]
    results = [city for city in cities if query.lower() in city.lower()]
    
    return templates.TemplateResponse(
        "htmx/search_results.html",
        {
            "request": request,
            "results": results
        }
    )

@router.get("/weather-card/{city}")
async def weather_card(request: Request, city: str):
    """动态加载天气卡片"""
    return templates.TemplateResponse(
        "htmx/weather_card.html",
        {
            "request": request,
            "city": city
        }
    ) 