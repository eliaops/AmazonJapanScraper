"""
Windows构建脚本 - 使用PyInstaller创建独立的Windows可执行文件
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
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 清理目录: {dir_name}")
            shutil.rmtree(dir_name)

def create_spec_file():
    """创建PyInstaller规格文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'requests',
        'beautifulsoup4',
        'bs4',
        'pandas',
        'openpyxl',
        'lxml',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
        'soupsieve',
        'et_xmlfile',
        'numpy',
        'python_dateutil',
        'pytz',
        'six'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
        'unittest',
        'test',
        'tests',
        'distutils',
        'setuptools',
        'pip',
        'wheel',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Amazon_Japan_Scraper_v2.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # 禁用UPX压缩，避免兼容性问题
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 设置为False隐藏控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open('amazon_scraper.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("✅ 创建PyInstaller规格文件")

def create_version_info():
    """创建版本信息文件"""
    version_content = '''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
# filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
# Set not needed items to zero 0.
filevers=(2,0,0,0),
prodvers=(2,0,0,0),
# Contains a bitmask that specifies the valid bits 'flags'r
mask=0x3f,
# Contains a bitmask that specifies the Boolean attributes of the file.
flags=0x0,
# The operating system for which this file was designed.
# 0x4 - NT and there is no need to change it.
OS=0x4,
# The general type of file.
# 0x1 - the file is an application.
fileType=0x1,
# The function of the file.
# 0x0 - the function is not defined for this fileType
subtype=0x0,
# Creation date and time stamp.
date=(0, 0)
),
  kids=[
StringFileInfo(
  [
  StringTable(
    u'040904B0',
    [StringStruct(u'CompanyName', u'Amazon Scraper Team'),
    StringStruct(u'FileDescription', u'Amazon Japan 卖家信息提取工具'),
    StringStruct(u'FileVersion', u'2.0.0.0'),
    StringStruct(u'InternalName', u'Amazon Japan Scraper'),
    StringStruct(u'LegalCopyright', u'Copyright © 2024 Amazon Scraper Team'),
    StringStruct(u'OriginalFilename', u'Amazon_Japan_Scraper_v2.0.exe'),
    StringStruct(u'ProductName', u'Amazon Japan Scraper'),
    StringStruct(u'ProductVersion', u'2.0.0.0')])
  ]), 
VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)'''
    
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_content)
    print("✅ 创建版本信息文件")

def build_executable():
    """构建可执行文件"""
    print("🚀 开始构建Windows可执行文件...")
    print("="*60)
    
    # 检查Python环境
    print(f"Python版本: {sys.version}")
    print(f"当前工作目录: {os.getcwd()}")
    
    # 清理构建目录
    clean_build_dirs()
    
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
    
    # 创建必要文件
    create_spec_file()
    create_version_info()
    
    # 使用PyInstaller构建
    build_command = "pyinstaller --clean --noconfirm amazon_scraper.spec"
    
    if not run_command(build_command, "PyInstaller构建"):
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

## 功能特点
- 🛒 支持Amazon日本站产品搜索
- 🌍 多语言卖家信息提取（中英日韩）
- 📊 详细卖家信息（Business Name、电话、地址、代表姓名、商店名）
- 📋 数据导出（Excel/CSV格式）
- 🎨 现代化用户界面

## 使用方法
1. 双击运行 Amazon_Japan_Scraper_v2.0.exe
2. 选择商品类目或输入自定义关键词
3. 设置搜索页数和最大产品数
4. 点击"开始搜索"按钮
5. 等待搜索完成后，点击"导出数据"保存结果

## 系统要求
- Windows 10 或更高版本
- 网络连接

## 注意事项
- 请合理使用，避免频繁请求
- 建议搜索间隔设置适当延迟
- 数据仅供学习和研究使用

## 版本信息
版本: 2.0.0
更新日期: 2024年
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
