@echo off
chcp 65001
echo ================================================
echo 亚马逊日本站卖家信息提取工具 - 依赖安装脚本
echo ================================================
echo.

echo 正在检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未找到Python环境！
    echo 请先安装Python 3.7或更高版本
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python环境检查通过
echo.

echo 正在升级pip...
python -m pip install --upgrade pip

echo.
echo 正在安装依赖包...
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo 依赖安装失败！请检查网络连接或手动安装
    pause
    exit /b 1
)

echo.
echo ================================================
echo 依赖安装完成！
echo 现在可以运行程序了：python main.py
echo ================================================
pause
