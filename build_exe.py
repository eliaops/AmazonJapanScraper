#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build script to create Windows executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil

def build_executable():
    """构建Windows可执行文件"""
    
    print("开始构建Windows可执行文件...")
    
    # PyInstaller命令
    cmd = [
        "pyinstaller",
        "--onefile",  # 打包成单个文件
        "--windowed",  # 不显示控制台窗口
        "--name=Amazon日本站卖家信息提取工具",
        "--icon=icon.ico",  # 如果有图标文件
        "--add-data=requirements.txt;.",
        "main.py"
    ]
    
    try:
        # 运行PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("构建成功！")
        print(result.stdout)
        
        # 创建发布目录
        dist_dir = "release"
        if os.path.exists(dist_dir):
            shutil.rmtree(dist_dir)
        os.makedirs(dist_dir)
        
        # 复制可执行文件
        exe_name = "Amazon日本站卖家信息提取工具.exe"
        src_exe = os.path.join("dist", exe_name)
        dst_exe = os.path.join(dist_dir, exe_name)
        
        if os.path.exists(src_exe):
            shutil.copy2(src_exe, dst_exe)
            print(f"可执行文件已复制到: {dst_exe}")
        
        # 复制说明文件
        readme_files = ["README.md", "使用说明.txt"]
        for readme in readme_files:
            if os.path.exists(readme):
                shutil.copy2(readme, dist_dir)
        
        print(f"\n构建完成！发布文件位于: {os.path.abspath(dist_dir)}")
        
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False
    except Exception as e:
        print(f"构建过程中出现错误: {e}")
        return False
    
    return True

def install_pyinstaller():
    """安装PyInstaller"""
    try:
        import PyInstaller
        print("PyInstaller已安装")
        return True
    except ImportError:
        print("正在安装PyInstaller...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("PyInstaller安装成功")
            return True
        except subprocess.CalledProcessError:
            print("PyInstaller安装失败，请手动安装: pip install pyinstaller")
            return False

if __name__ == "__main__":
    print("=" * 50)
    print("亚马逊日本站卖家信息提取工具 - 构建脚本")
    print("=" * 50)
    
    # 检查并安装PyInstaller
    if not install_pyinstaller():
        sys.exit(1)
    
    # 构建可执行文件
    if build_executable():
        print("\n构建成功！可以将release目录中的文件分发给用户。")
    else:
        print("\n构建失败！请检查错误信息。")
        sys.exit(1)
