"""文档生成脚本"""
import sys
import os
from pathlib import Path
import logging
import mkdocs_gen_files
from typing import Dict, Any

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocsGenerator:
    """文档生成器"""
    
    def __init__(self):
        # 确保在项目根目录下运行
        self.project_root = Path(__file__).parent.parent
        os.chdir(self.project_root)  # 切换到项目根目录
        
        self.docs_root = self.project_root / "docs"
        
        # 添加项目根目录到 Python 路径
        sys.path.insert(0, str(self.project_root))
        
        # 定义文档目录
        self.dirs = {
            'api': self.docs_root / 'api',
            'guide': self.docs_root / 'guide',
            'dev': self.docs_root / 'dev',
            'reference': self.docs_root / 'reference'
        }

    def ensure_dirs(self) -> None:
        """确保所有必要的目录存在"""
        for dir_path in self.dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")

    def generate_guide_docs(self) -> None:
        """生成用户指南文档"""
        guide_files = {
            'getting-started.md': """# Getting Started

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

1. Copy `.env.example` to `.env`
2. Configure your environment variables

## Running the Application

```bash
python run.py
```
""",
            'usage.md': """# Usage Guide

## Searching Weather
1. Enter a city name
2. Click the search button

## Viewing Details
Click on weather cards to view detailed information
"""
        }
        
        self._write_docs(self.dirs['guide'], guide_files)

    def generate_api_docs(self) -> None:
        """生成 API 文档"""
        api_files = {
            'index.md': """# API Documentation

This section contains the complete API documentation for the Weather Dashboard.

## Available Endpoints

- `/api/weather/{city}` - Get weather data for a specific city
""",
            'weather.md': """# Weather API

## Endpoints

### GET /api/weather/{city}

Get current weather and forecast for a specific city.

#### Parameters
- `city` (string): City name in English

#### Response
```json
{
    "current": {
        "temp": 20.5,
        "humidity": 65,
        "wind_speed": 5.2
    },
    "forecast": [...]
}
```
"""
        }
        
        self._write_docs(self.dirs['api'], api_files)

    def generate_dev_docs(self) -> None:
        """生成开发文档"""
        dev_files = {
            'index.md': """# Development Guide

## Project Structure

```
weather-dashboard/
├── app/
│   ├── api/
│   ├── services/
│   ├── static/
│   └── templates/
├── docs/
└── tests/
```
""",
            'contributing.md': """# Contributing

## Development Setup
1. Create virtual environment
2. Install dependencies
3. Configure development tools

## Code Style
- Use Black for formatting
- Use Flake8 for linting
- Write unit tests
"""
        }
        
        self._write_docs(self.dirs['dev'], dev_files)

    def generate_reference_docs(self) -> None:
        """生成 API 参考文档"""
        modules = [
            "app.main",
            "app.api.weather",
            "app.services.weather"
        ]

        nav = ["# API Reference\n"]
        
        for module in modules:
            module_path = module.replace(".", "/")
            doc_path = f"reference/{module_path}.md"
            
            # 确保父目录存在
            doc_file = self.docs_root / doc_path
            doc_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 修改导航链接格式
            nav.append(f"* [{module}]({module_path}.md)")

            with mkdocs_gen_files.open(doc_path, "w") as f:
                f.write(f"# {module}\n\n")
                f.write(f"::: {module}")
                logger.info(f"Generated reference doc: {doc_path}")

        # 写入导航文件
        with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
            nav_file.write("\n".join(nav))
            logger.info("Generated reference summary")

    def _write_docs(self, dir_path: Path, files: Dict[str, str]) -> None:
        """写入文档文件"""
        for filename, content in files.items():
            file_path = dir_path / filename
            file_path.write_text(content, encoding='utf-8')
            logger.info(f"Generated: {file_path}")

    def generate_all(self) -> None:
        """生成所有文档"""
        try:
            self.ensure_dirs()
            self.generate_guide_docs()
            self.generate_api_docs()
            self.generate_dev_docs()
            self.generate_reference_docs()
            logger.info("All documentation generated successfully")
        except Exception as e:
            logger.error(f"Error generating documentation: {e}")
            raise

def main():
    """主函数"""
    try:
        generator = DocsGenerator()
        generator.generate_all()
    except Exception as e:
        logger.error(f"Documentation generation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 