#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Amazon Japan Scraper - Ultimate Version Build Script
构建终极版 v4.0
"""

import os
import sys
import subprocess
import shutil

def clean_dirs():
    """清理构建目录"""
    for dir_name in ['build', 'dist', 'release_ultimate']:
        if os.path.exists(dir_name):
            print(f"Cleaning: {dir_name}")
            shutil.rmtree(dir_name)

def build_ultimate():
    """构建终极版可执行文件"""
    print("Amazon Japan Scraper - Ultimate Version v4.0 Build")
    print("=" * 60)
    clean_dirs()
    
    # 检查主文件
    if not os.path.exists('main_ultimate.py'):
        print("ERROR: main_ultimate.py not found")
        return False
    
    # 构建命令 - 跨平台兼容
    pyinstaller_cmd = 'pyinstaller'
    if not os.path.exists('/usr/local/bin/pyinstaller') and os.path.exists('/Users/evan/Library/Python/3.9/bin/pyinstaller'):
        pyinstaller_cmd = '/Users/evan/Library/Python/3.9/bin/pyinstaller'
    
    cmd = [
        pyinstaller_cmd,
        '--onefile',
        '--windowed',
        '--name=Amazon_Japan_Scraper_v4.0_Ultimate',
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=requests',
        '--hidden-import=bs4',
        '--hidden-import=pandas',
        '--hidden-import=openpyxl',
        '--hidden-import=concurrent.futures',
        '--hidden-import=urllib3',
        '--hidden-import=certifi',
        '--exclude-module=matplotlib',
        '--exclude-module=scipy',
        '--exclude-module=numpy',
        '--clean',
        '--noconfirm',
        'main_ultimate.py'
    ]
    
    print("Building Ultimate v4.0...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        # 设置正确的编码以避免Windows编码问题
        encoding = 'utf-8' if sys.platform != 'win32' else 'cp1252'
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, 
                              encoding=encoding, errors='replace')
        print("Build successful!")
        
        # 检查结果 - 跨平台兼容
        if sys.platform == 'win32':
            exe_name = 'Amazon_Japan_Scraper_v4.0_Ultimate.exe'
        else:
            exe_name = 'Amazon_Japan_Scraper_v4.0_Ultimate'
        
        exe_path = f'dist/{exe_name}'
        
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"Executable created: {exe_path}")
            print(f"Size: {size_mb:.1f} MB")
            
            # 验证文件类型 (仅在Windows上)
            if sys.platform == 'win32':
                try:
                    with open(exe_path, 'rb') as f:
                        header = f.read(2)
                        if header == b'MZ':
                            print("✅ Valid Windows executable (MZ header found)")
                        else:
                            print("⚠️ Warning: File may not be a valid Windows executable")
                except Exception as e:
                    print(f"⚠️ Could not verify file header: {e}")
            
            # 创建发布目录
            os.makedirs('release_ultimate', exist_ok=True)
            
            # 复制文件，确保Windows版本有.exe扩展名
            if sys.platform == 'win32':
                release_name = 'Amazon_Japan_Scraper_v4.0_Ultimate.exe'
            else:
                release_name = 'Amazon_Japan_Scraper_v4.0_Ultimate'
            
            shutil.copy2(exe_path, f'release_ultimate/{release_name}')
            print(f"Copied to release directory: release_ultimate/{release_name}")
            
            # 创建说明文件
            with open('release_ultimate/README.txt', 'w', encoding='utf-8') as f:
                f.write("""# Amazon Japan Scraper v4.0 - 终极版

## 🚀 v4.0 终极版特性

### 🎯 核心改进
- 🔍 扩大关键词搜索范围，支持更多小商品类别
- ♾️ 无限制连续搜索，想搜多久搜多久
- 💾 实时保存功能，一边搜索一边保存数据
- 🧠 四层智能卖家信息提取算法
- 🖥️ 支持后台运行，可以离开桌面

### 🔍 搜索能力提升
- 支持任何商品关键词：手机壳、数据线、小商品等
- 多种搜索策略：默认、分类、品牌、价格区间
- 智能去重，避免重复数据
- 扩展产品选择器，覆盖更多商品类型

### 💾 数据管理
- 每50个产品自动保存一次
- 同时生成Excel和CSV格式
- 数据保存在amazon_data文件夹
- 支持断点续传，不怕意外中断

### 🧠 卖家信息提取算法
1. **智能关键词提取** - 基于上下文分析
2. **HTML结构提取** - 利用页面结构
3. **正则表达式提取** - 精准模式匹配
4. **深度文本分析** - 复杂文本处理

### 📊 提取字段
- 公司名称 (Business Name)
- 电话号码 (咨询用电话号码)
- 详细地址 (包含邮编)
- 代表人姓名 (购物代表的姓名)
- 店铺名称
- 电子邮箱
- 传真号码

### 🚀 使用方法
1. 启动程序
2. 输入任何商品关键词
3. 点击"开始无限搜索"
4. 可以最小化窗口，后台运行
5. 数据自动保存，随时可以停止

### ⚡ 性能特点
- 智能延迟控制，避免被封
- 并发处理，提高效率
- 内存优化，长时间稳定运行
- 实时进度显示

### 📁 输出文件
- 产品信息：包含标题、价格、评分等
- 卖家信息：包含完整联系方式
- 自动生成时间戳文件名

版本: 4.0.0 - 终极版
构建时间: 2024年
""")
            
            print(f"Release package created in 'release_ultimate' directory")
            return True
        else:
            print("ERROR: Executable not found after build")
            return False
    except subprocess.CalledProcessError as e:
        error_msg = str(e.stderr) if e.stderr else "Unknown build error"
        print(f"Build error: {error_msg}")
        return False
    except Exception as e:
        error_msg = str(e).encode('ascii', errors='replace').decode('ascii')
        print(f"An unexpected error occurred: {error_msg}")
        return False

if __name__ == "__main__":
    if not build_ultimate():
        sys.exit(1)
