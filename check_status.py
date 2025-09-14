"""
项目状态检查脚本 - 验证所有组件是否准备就绪
"""

import os
import sys
from pathlib import Path

def check_files():
    """检查必要文件是否存在"""
    print("📁 检查项目文件...")
    
    required_files = {
        'main.py': '主程序文件',
        'requirements.txt': '依赖配置',
        'build_simple.py': '简化构建脚本',
        'build_windows.py': '完整构建脚本',
        'README.md': '项目说明',
        'LICENSE': '许可证',
        '.gitignore': 'Git忽略规则',
        '.github/workflows/build-windows.yml': 'GitHub Actions配置',
        'BUILD_FIX_SUMMARY.md': '构建修复总结'
    }
    
    missing_files = []
    for file_path, description in required_files.items():
        if os.path.exists(file_path):
            print(f"  ✅ {file_path} - {description}")
        else:
            print(f"  ❌ {file_path} - {description} (缺失)")
            missing_files.append(file_path)
    
    return len(missing_files) == 0, missing_files

def check_dependencies():
    """检查Python依赖"""
    print("\n📦 检查Python依赖...")
    
    required_packages = [
        ('tkinter', 'GUI框架'),
        ('requests', 'HTTP请求'),
        ('bs4', 'HTML解析'),
        ('pandas', '数据处理'),
        ('openpyxl', 'Excel操作'),
        ('lxml', 'XML解析')
    ]
    
    missing_packages = []
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package} - {description}")
        except ImportError:
            print(f"  ❌ {package} - {description} (缺失)")
            missing_packages.append(package)
    
    return len(missing_packages) == 0, missing_packages

def check_github_actions():
    """检查GitHub Actions配置"""
    print("\n🚀 检查GitHub Actions配置...")
    
    workflow_file = '.github/workflows/build-windows.yml'
    if not os.path.exists(workflow_file):
        print("  ❌ GitHub Actions配置文件不存在")
        return False
    
    with open(workflow_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ('actions/upload-artifact@v4', '使用最新的artifact上传action'),
        ('actions/setup-python@v5', '使用最新的Python设置action'),
        ('windows-2022', '使用固定的Windows版本'),
        ('python-version: \'3.11\'', '使用Python 3.11'),
        ('build_simple.py', '使用简化构建脚本')
    ]
    
    all_good = True
    for check, description in checks:
        if check in content:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} (未找到: {check})")
            all_good = False
    
    return all_good

def check_main_module():
    """检查主模块是否可以导入"""
    print("\n🔍 检查主模块...")
    
    try:
        sys.path.insert(0, '.')
        from main import AmazonJapanScraper, AmazonScraperGUI
        print("  ✅ 主模块导入成功")
        
        # 测试基本实例化
        scraper = AmazonJapanScraper()
        print("  ✅ 爬虫类实例化成功")
        
        return True
    except Exception as e:
        print(f"  ❌ 主模块导入失败: {e}")
        return False

def main():
    """主检查函数"""
    print("🔍 Amazon Japan Scraper - 项目状态检查")
    print("="*60)
    
    checks_passed = 0
    total_checks = 4
    
    # 检查文件
    files_ok, missing_files = check_files()
    if files_ok:
        checks_passed += 1
    else:
        print(f"\n⚠️ 缺失文件: {', '.join(missing_files)}")
    
    # 检查依赖
    deps_ok, missing_deps = check_dependencies()
    if deps_ok:
        checks_passed += 1
    else:
        print(f"\n⚠️ 缺失依赖: {', '.join(missing_deps)}")
        print("请运行: pip install -r requirements.txt")
    
    # 检查GitHub Actions
    if check_github_actions():
        checks_passed += 1
    else:
        print("\n⚠️ GitHub Actions配置需要检查")
    
    # 检查主模块
    if check_main_module():
        checks_passed += 1
    else:
        print("\n⚠️ 主模块存在问题")
    
    # 总结
    print("\n" + "="*60)
    print(f"📊 检查结果: {checks_passed}/{total_checks} 通过")
    
    if checks_passed == total_checks:
        print("🎉 所有检查通过！项目已准备就绪。")
        print("\n📋 下一步:")
        print("  1. 推送代码到GitHub: git add . && git commit -m 'Fix build issues' && git push")
        print("  2. 创建版本标签: git tag v2.0.1 && git push origin v2.0.1")
        print("  3. 检查GitHub Actions构建结果")
        return True
    else:
        print("❌ 部分检查失败，请修复问题后重新检查。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
