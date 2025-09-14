"""
构建简化版本的Amazon Japan Scraper
"""

import os
import sys
import subprocess
import shutil

def main():
    print("Amazon Japan Scraper - Simplified Version Build")
    print("=" * 60)
    
    # 清理之前的构建
    for dirname in ['build', 'dist', '__pycache__', 'release_simplified']:
        if os.path.exists(dirname):
            print(f"Cleaning: {dirname}")
            shutil.rmtree(dirname)
    
    # 检查主文件
    if not os.path.exists('main_simplified.py'):
        print("ERROR: main_simplified.py not found")
        return False
    
    # 构建命令
    cmd = [
        '/Users/evan/Library/Python/3.9/bin/pyinstaller',
        '--onefile',
        '--windowed', 
        '--name=Amazon_Japan_Scraper_v3.1_Enhanced',
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=requests',
        '--hidden-import=bs4',
        '--hidden-import=pandas',
        '--hidden-import=openpyxl',
        '--exclude-module=matplotlib',
        '--exclude-module=scipy',
        '--clean',
        'main_simplified.py'
    ]
    
    print("Building simplified version...")
    print("Command:", ' '.join(cmd))
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        
        # 检查结果
        exe_name = 'Amazon_Japan_Scraper_v3.1_Enhanced'
        exe_path = f'dist/{exe_name}'
        
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"Executable created: {exe_path}")
            print(f"Size: {size_mb:.1f} MB")
            
            # 创建发布目录
            os.makedirs('release_simplified', exist_ok=True)
            shutil.copy2(exe_path, f'release_simplified/{exe_name}')
            
            # 创建说明文件
            with open('release_simplified/README.txt', 'w', encoding='utf-8') as f:
                f.write("""# Amazon Japan Scraper v3.1 - 增强提取版

## 🎉 v3.1 增强更新
- 🔍 全新智能卖家信息提取算法
- 📞 精准电话号码识别和提取
- 🏢 完整公司地址和代表人信息
- 🏪 准确店铺名称提取
- 🧠 基于关键词关联的上下文分析
- 📊 三层提取策略确保信息完整性
- 简化业务逻辑，移除复杂分类系统
- 分批处理，支持10000+产品不崩溃
- 内存优化，稳定运行大规模数据
- 直接关键词搜索，更符合用户习惯

## 🚀 使用方法
1. 双击运行程序
2. 输入搜索关键词（如：电脑、笔记本、手机）
3. 设置页数和产品数量
4. 点击开始搜索

## ⚙️ 推荐配置
- 小规模测试：20页，100产品
- 中等规模：50页，500产品  
- 大规模：100页，2000产品

## 🛡️ 稳定性保证
- 分批处理，每批20个产品
- 内存自动清理，不会溢出
- 错误自动恢复，单个失败不影响整体

版本: 3.0.0 - 简化高性能版
""")
            
            print(f"Release package created in 'release_simplified' directory")
            return True
        else:
            print("ERROR: Executable not found after build")
            return False
            
    except subprocess.CalledProcessError as e:
        print("Build failed!")
        print("Error:", e.stderr if e.stderr else str(e))
        return False
    except Exception as e:
        print("Build error:", str(e))
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
