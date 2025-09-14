@echo off
chcp 65001 >nul
echo ========================================
echo Amazon Japan Scraper - Windows构建工具
echo ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.9或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python已安装
python --version

:: 升级pip
echo.
echo 📦 升级pip...
python -m pip install --upgrade pip

:: 安装依赖
echo.
echo 📦 安装项目依赖...
pip install -r requirements.txt

:: 安装构建工具
echo.
echo 🔧 安装构建工具...
pip install pyinstaller

:: 检查依赖是否安装成功
echo.
echo 🔍 检查依赖包...
python -c "
import sys
packages = ['requests', 'beautifulsoup4', 'pandas', 'openpyxl', 'lxml', 'pyinstaller']
missing = []
for pkg in packages:
    try:
        __import__(pkg.replace('-', '_'))
        print(f'✅ {pkg}')
    except ImportError:
        print(f'❌ {pkg}')
        missing.append(pkg)

if missing:
    print(f'\\n⚠️ 缺失包: {missing}')
    sys.exit(1)
else:
    print('\\n🎉 所有依赖包已安装完成!')
"

if errorlevel 1 (
    echo.
    echo ❌ 依赖安装失败，请检查网络连接或手动安装
    pause
    exit /b 1
)

:: 询问是否立即构建
echo.
set /p build_now="是否立即构建Windows可执行文件? (y/n): "
if /i "%build_now%"=="y" (
    echo.
    echo 🚀 开始构建...
    echo 选择构建方式:
    echo 1. 简化构建 (推荐)
    echo 2. 完整构建
    set /p build_type="请选择 (1/2): "
    
    if "!build_type!"=="1" (
        python build_simple.py
    ) else (
        python build_windows.py
    )
    
    if errorlevel 1 (
        echo.
        echo ❌ 构建失败
        pause
        exit /b 1
    ) else (
        echo.
        echo 🎉 构建成功!
        echo 📁 可执行文件位于 release 目录
        echo.
        echo 是否打开release目录?
        set /p open_folder="(y/n): "
        if /i "!open_folder!"=="y" (
            start explorer release
        )
    )
)

echo.
echo ✅ 安装完成!
echo.
echo 📋 使用说明:
echo   - 运行程序: python main.py
echo   - 构建exe: python build_windows.py
echo   - 查看帮助: python main.py --help
echo.
pause
