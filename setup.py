"""
Amazon Japan Scraper - Windows安装程序配置
支持多语言卖家信息提取的Amazon日本站爬虫工具
"""

import sys
import os
from cx_Freeze import setup, Executable

# 应用程序信息
APP_NAME = "Amazon Japan Scraper"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "Amazon Japan 卖家信息提取工具 - 多语言增强版"
APP_AUTHOR = "Amazon Scraper Team"
APP_COPYRIGHT = "Copyright © 2024 Amazon Scraper Team"

# 确定基础路径
if getattr(sys, 'frozen', False):
    # 如果是打包后的可执行文件
    base_path = sys._MEIPASS
else:
    # 如果是开发环境
    base_path = os.path.dirname(os.path.abspath(__file__))

# 需要包含的文件和目录
include_files = [
    # 可以添加图标、配置文件等
    # ("icon.ico", "icon.ico"),
    # ("config", "config"),
]

# 需要包含的包
packages = [
    "tkinter",
    "requests", 
    "beautifulsoup4",
    "pandas",
    "openpyxl",
    "lxml",
    "urllib3",
    "certifi",
    "charset_normalizer",
    "idna",
    "soupsieve",
    "et_xmlfile",
    "numpy",
    "python_dateutil",
    "pytz",
    "six"
]

# 需要排除的模块（减少打包大小）
excludes = [
    "matplotlib",
    "scipy",
    "IPython",
    "jupyter",
    "notebook",
    "pytest",
    "unittest",
    "test",
    "tests",
    "distutils",
    "setuptools",
    "pip",
    "wheel"
]

# 构建选项
build_exe_options = {
    "packages": packages,
    "excludes": excludes,
    "include_files": include_files,
    "optimize": 2,
    "include_msvcrt": True,
    "build_exe": "build/Amazon_Japan_Scraper_v2.0",
}

# 可执行文件配置
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # 使用GUI基础，隐藏控制台窗口

executable = Executable(
    script="main.py",
    base=base,
    target_name="Amazon_Japan_Scraper.exe",
    icon=None,  # 可以添加图标文件路径
    copyright=APP_COPYRIGHT,
    shortcut_name=APP_NAME,
    shortcut_dir="DesktopFolder",
)

# MSI安装程序选项
bdist_msi_options = {
    "upgrade_code": "{12345678-1234-5678-9012-123456789012}",
    "add_to_path": False,
    "initial_target_dir": r"[ProgramFilesFolder]\Amazon Japan Scraper",
    "install_icon": None,  # 可以添加图标文件路径
}

setup(
    name=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    author=APP_AUTHOR,
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options,
    },
    executables=[executable],
)