@echo off
chcp 65001
echo 启动亚马逊日本站卖家信息提取工具...
echo.

python main.py

if %errorlevel% neq 0 (
    echo.
    echo 程序运行出现错误！
    echo 请确保已安装所需依赖：运行 install_dependencies.bat
    pause
)
