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
    print(f"\n[INFO] {description}...")
    print(f"Command: {command}")
    
    try:
        # 在Windows上使用cp1252编码，其他系统使用utf-8
        encoding = 'cp1252' if sys.platform == 'win32' else 'utf-8'
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True, 
                              encoding=encoding, errors='replace')
        print(f"[SUCCESS] {description} completed")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} failed")
        print(f"Exit code: {e.returncode}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"[ERROR] {description} exception: {e}")
        return False

def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = ['build', 'dist', '__pycache__', 'release']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"[CLEAN] Removing directory: {dir_name}")
            shutil.rmtree(dir_name)

def build_executable():
    """构建可执行文件"""
    print("Building Windows executable (simplified version)...")
    print("="*60)
    
    # 检查Python环境
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    
    # 清理构建目录
    clean_build_dirs()
    
    # 检查主文件
    if not os.path.exists('main.py'):
        print("[ERROR] main.py file not found")
        return False
    
    # 检查依赖
    print("\n[CHECK] Checking dependencies...")
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
            print(f"[OK] {package}")
        except ImportError:
            print(f"[MISSING] {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n[WARNING] Missing packages: {', '.join(missing_packages)}")
        print("Please install with:")
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
    
    if not run_command(build_cmd_str, "PyInstaller Build"):
        return False
    
    # 检查构建结果
    exe_path = "dist/Amazon_Japan_Scraper_v2.0.exe"
    if os.path.exists(exe_path):
        file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
        print(f"\n[SUCCESS] Build completed!")
        print(f"[INFO] Executable location: {os.path.abspath(exe_path)}")
        print(f"[INFO] File size: {file_size:.1f} MB")
        
        # 创建发布目录
        release_dir = "release"
        if os.path.exists(release_dir):
            shutil.rmtree(release_dir)
        os.makedirs(release_dir)
        
        # 复制可执行文件
        shutil.copy2(exe_path, f"{release_dir}/Amazon_Japan_Scraper_v2.0.exe")
        
        # 创建说明文件
        readme_content = """# Amazon Japan Seller Information Extractor v2.0

## How to Use
1. Double-click Amazon_Japan_Scraper_v2.0.exe to run
2. Select product category or enter custom keywords
3. Set search pages and maximum products
4. Click "Start Search" button
5. After search completes, click "Export Data" to save results

## Features
- Amazon Japan product search support
- Multi-language seller information extraction (Chinese/English/Japanese/Korean)
- Detailed seller information extraction
- Data export (Excel/CSV formats)
- Modern user interface

## System Requirements
- Windows 10 or higher
- Internet connection

## Notes
- Please use responsibly, avoid frequent requests
- Data for learning and research purposes only
- Follow website terms of service

Version: 2.0.0
"""
        
        with open(f"{release_dir}/README.txt", 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"[INFO] Release package created: {os.path.abspath(release_dir)}")
        return True
    else:
        print("[ERROR] Build failed, executable not found")
        return False

if __name__ == "__main__":
    success = build_executable()
    
    if success:
        print("\n[SUCCESS] Build completed!")
        print("[INFO] Check the release directory for the final executable")
    else:
        print("\n[ERROR] Build failed!")
        sys.exit(1)
