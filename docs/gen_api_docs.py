"""生成 API 文档"""
from pathlib import Path
import importlib
import inspect
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ensure_dir_exists(path: Path) -> None:
    """确保目录存在，如果不存在则创建"""
    path.mkdir(parents=True, exist_ok=True)

def generate_api_docs():
    """生成 API 文档"""
    try:
        # 设置文档根目录
        docs_root = Path(__file__).parent
        
        # 创建所需的目录结构
        dirs = {
            'api': docs_root / 'api',
            'guide': docs_root / 'guide',
            'dev': docs_root / 'dev'
        }
        
        # 创建所有必要的目录
        for dir_path in dirs.values():
            ensure_dir_exists(dir_path)
            logger.info(f"Created directory: {dir_path}")

        # 生成 API 索引
        with open(dirs['api'] / "index.md", "w", encoding="utf-8") as f:
            f.write("""# API 文档

这里包含了天气仪表盘应用的 API 文档。

## 模块列表

- [主模块](main.md)
- [天气服务](weather.md)
""")
        logger.info("Generated API index")

        # 生成主模块文档
        with open(dirs['api'] / "main.md", "w", encoding="utf-8") as f:
            f.write("""# 主模块 API

::: app.main
""")
        logger.info("Generated main module documentation")

        # 生成天气服务文档
        with open(dirs['api'] / "weather.md", "w", encoding="utf-8") as f:
            f.write("""# 天气服务 API

::: app.services.weather
""")
        logger.info("Generated weather service documentation")

        # 生成基本的指南文档
        guide_content = """# 用户指南

## 快速开始

1. 安装依赖
2. 配置环境
3. 运行应用

详细说明请参考各个章节。
"""
        with open(dirs['guide'] / "index.md", "w", encoding="utf-8") as f:
            f.write(guide_content)
        logger.info("Generated guide documentation")

        # 生成开发文档
        dev_content = """# 开发文档

## 项目结构

- app/: 应用源码
- docs/: 文档
- tests/: 测试用例

## 开发指南

请参考具体章节了解详细信息。
"""
        with open(dirs['dev'] / "index.md", "w", encoding="utf-8") as f:
            f.write(dev_content)
        logger.info("Generated development documentation")

        logger.info("All documentation generated successfully")

    except Exception as e:
        logger.error(f"Error generating documentation: {e}", exc_info=True)
        raise

def main():
    """主函数"""
    try:
        generate_api_docs()
    except Exception as e:
        logger.error(f"Documentation generation failed: {e}")
        raise SystemExit(1)

if __name__ == "__main__":
    main() 