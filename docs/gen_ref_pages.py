"""生成 API 参考文档"""
import sys
from pathlib import Path
import mkdocs_gen_files

def generate_ref_pages():
    """生成 API 参考文档"""
    # 添加项目根目录到 Python 路径
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    # 创建 reference 目录
    reference_dir = Path("docs/reference")
    reference_dir.mkdir(exist_ok=True, parents=True)

    # 生成 SUMMARY.md
    nav = ["# API 参考文档\n"]
    
    # 遍历项目模块
    modules = [
        "app.main",
        "app.api.weather", 
        "app.services.weather"
    ]

    for module in modules:
        module_path = module.replace(".", "/")
        doc_path = f"reference/{module_path}.md"
        
        nav.append(f"* [{module}]({doc_path})")

        with mkdocs_gen_files.open(doc_path, "w") as f:
            f.write(f"# {module}\n\n")
            f.write(f"::: {module}")

    # 写入导航文件
    with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
        nav_file.write("\n".join(nav))

    # 生成 __init__ 文件以使 reference 成为一个 Python 包
    with mkdocs_gen_files.open("reference/__init__.py", "w") as init_file:
        init_file.write('"""API reference documentation."""\n')

def main():
    """主函数"""
    try:
        generate_ref_pages()
    except Exception as e:
        print(f"Error generating reference pages: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 