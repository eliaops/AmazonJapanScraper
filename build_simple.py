"""
简化的Windows构建脚本 - 使用PyInstaller的基本命令
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """运行命令并处理错误"""
    print(f"\n🔄 {description}...")
    print(f"执行命令: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True, encoding='utf-8')
        print(f"✅ {description} 成功完成")
        if result.stdout:
            print(f"输出: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败")
        print(f"错误代码: {e.returncode}")
        print(f"错误输出: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ {description} 出现异常: {e}")
        return False

def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = ['build', 'dist', '__pycache__', 'release']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 清理目录: {dir_name}")
            shutil.rmtree(dir_name)

def build_executable():
    """构建可执行文件"""
    print("🚀 开始构建Windows可执行文件（简化版）...")
    print("="*60)
    
    # 检查Python环境
    print(f"Python版本: {sys.version}")
    print(f"当前工作目录: {os.getcwd()}")
    
    # 清理构建目录
    clean_build_dirs()
    
    # 检查主文件
    if not os.path.exists('main.py'):
        print("❌ 未找到main.py文件")
        return False
    
    # 检查依赖
    print("\n📦 检查依赖包...")
    required_packages = [
        'pyinstaller',
        'requests', 
        'beautifulsoup4',
        'pandas',
        'openpyxl',
        'lxml'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (缺失)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ 缺失依赖包: {', '.join(missing_packages)}")
        print("请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    # 使用PyInstaller简单命令构建
    build_command = [
        "pyinstaller",
        "--onefile",  # 单文件模式
        "--windowed",  # 无控制台窗口
        "--name=Amazon_Japan_Scraper_v2.0",
        "--add-data=requirements.txt;.",  # 包含requirements.txt
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk", 
        "--hidden-import=requests",
        "--hidden-import=beautifulsoup4",
        "--hidden-import=bs4",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=lxml",
        "--exclude-module=matplotlib",
        "--exclude-module=scipy",
        "--exclude-module=IPython",
        "--exclude-module=jupyter",
        "--exclude-module=pytest",
        "--clean",
        "main.py"
    ]
    
    build_cmd_str = " ".join(build_command)
    
    if not run_command(build_cmd_str, "PyInstaller构建"):
        return False
    
    # 检查构建结果
    exe_path = "dist/Amazon_Japan_Scraper_v2.0.exe"
    if os.path.exists(exe_path):
        file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
        print(f"\n🎉 构建成功!")
        print(f"📁 可执行文件位置: {os.path.abspath(exe_path)}")
        print(f"📊 文件大小: {file_size:.1f} MB")
        
        # 创建发布目录
        release_dir = "release"
        if os.path.exists(release_dir):
            shutil.rmtree(release_dir)
        os.makedirs(release_dir)
        
        # 复制可执行文件
        shutil.copy2(exe_path, f"{release_dir}/Amazon_Japan_Scraper_v2.0.exe")
        
        # 创建说明文件
        readme_content = """# Amazon Japan 卖家信息提取工具 v2.0

## 使用方法
1. 双击运行 Amazon_Japan_Scraper_v2.0.exe
2. 选择商品类目或输入自定义关键词
3. 设置搜索页数和最大产品数
4. 点击"开始搜索"按钮
5. 等待搜索完成后，点击"导出数据"保存结果

## 功能特点
- 🛒 支持Amazon日本站产品搜索
- 🌍 多语言卖家信息提取（中英日韩）
- 📊 详细卖家信息提取
- 📋 数据导出（Excel/CSV格式）
- 🎨 现代化用户界面

## 系统要求
- Windows 10 或更高版本
- 网络连接

## 注意事项
- 请合理使用，避免频繁请求
- 数据仅供学习和研究使用
- 遵守网站使用条款

版本: 2.0.0
"""
        
        with open(f"{release_dir}/README.txt", 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"📦 发布包已创建: {os.path.abspath(release_dir)}")
        return True
    else:
        print("❌ 构建失败，未找到可执行文件")
        return False

if __name__ == "__main__":
    success = build_executable()
    
    if success:
        print("\n🎉 构建完成!")
        print("📁 请查看 release 目录获取最终的可执行文件")
    else:
        print("\n❌ 构建失败!")
        sys.exit(1)
