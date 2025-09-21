#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断Windows可执行文件问题
Diagnose Windows Executable Issues
"""

import os
import subprocess
import sys

def analyze_problem():
    """分析可执行文件问题"""
    print("🔍 Windows可执行文件问题诊断")
    print("=" * 60)
    
    print("📋 问题描述:")
    print("  - 客户打开时需要选择打开方式")
    print("  - 之前版本没有这个问题")
    print("  - 文件关联可能有问题")
    
    print("\n🔍 可能的原因:")
    reasons = [
        "1. 文件没有正确的Windows可执行文件头",
        "2. PyInstaller构建参数不正确",
        "3. 文件在传输过程中被损坏",
        "4. 强制重命名破坏了文件结构",
        "5. 缺少必要的Windows可执行文件属性"
    ]
    
    for reason in reasons:
        print(f"  {reason}")
    
    print("\n🔧 GitHub Actions修复:")
    fixes = [
        "✅ 移除了强制重命名逻辑",
        "✅ 添加了文件签名验证 (MZ header)",
        "✅ 添加了PyInstaller构建验证",
        "✅ 使用--icon=NONE避免图标问题",
        "✅ 添加--noconfirm确保非交互式构建"
    ]
    
    for fix in fixes:
        print(f"  {fix}")

def check_pyinstaller_settings():
    """检查PyInstaller设置"""
    print("\n⚙️ PyInstaller设置分析")
    print("=" * 40)
    
    print("🔧 当前设置:")
    settings = [
        "--onefile: 单文件打包",
        "--windowed: Windows GUI应用",
        "--name: 指定输出文件名",
        "--icon=NONE: 不使用图标(避免问题)",
        "--clean: 清理临时文件",
        "--noconfirm: 非交互式构建"
    ]
    
    for setting in settings:
        print(f"  ✅ {setting}")
    
    print("\n❌ 可能有问题的设置:")
    issues = [
        "缺少--target-architecture参数",
        "可能需要--add-data参数",
        "可能需要--runtime-tmpdir参数"
    ]
    
    for issue in issues:
        print(f"  ⚠️ {issue}")

def suggest_solutions():
    """建议解决方案"""
    print("\n💡 解决方案建议")
    print("=" * 40)
    
    solutions = [
        {
            "问题": "文件关联问题",
            "解决": "确保PyInstaller生成正确的PE文件头"
        },
        {
            "问题": "构建环境问题", 
            "解决": "使用最新的PyInstaller版本和Python 3.11"
        },
        {
            "问题": "文件传输问题",
            "解决": "验证文件完整性和签名"
        },
        {
            "问题": "权限问题",
            "解决": "确保文件有执行权限"
        }
    ]
    
    for i, solution in enumerate(solutions, 1):
        print(f"  {i}. {solution['问题']}")
        print(f"     解决: {solution['解决']}")

def show_verification_steps():
    """显示验证步骤"""
    print("\n🧪 验证步骤")
    print("=" * 40)
    
    steps = [
        "1. 检查dist目录内容和文件大小",
        "2. 验证文件有MZ头签名(Windows可执行文件)",
        "3. 确认文件扩展名为.exe",
        "4. 检查文件权限和属性",
        "5. 测试文件是否可以直接运行"
    ]
    
    for step in steps:
        print(f"  {step}")
    
    print("\n📊 GitHub Actions现在会显示:")
    outputs = [
        "- dist目录的详细内容",
        "- 文件大小和创建时间", 
        "- 文件签名验证结果",
        "- 构建成功/失败状态"
    ]
    
    for output in outputs:
        print(f"  {output}")

def compare_versions():
    """版本对比"""
    print("\n📈 版本对比分析")
    print("=" * 40)
    
    print("🔄 变化分析:")
    changes = [
        {
            "版本": "v3.1",
            "状态": "正常工作",
            "构建": "简单复制dist文件"
        },
        {
            "版本": "v4.0",
            "状态": "需要选择打开方式",
            "构建": "添加了复杂的文件检查逻辑"
        },
        {
            "版本": "v4.0.2 (修复版)",
            "状态": "应该正常工作",
            "构建": "简化逻辑+文件验证"
        }
    ]
    
    for change in changes:
        print(f"  📦 {change['版本']}: {change['状态']}")
        print(f"     构建方式: {change['构建']}")

if __name__ == "__main__":
    analyze_problem()
    check_pyinstaller_settings()
    suggest_solutions()
    show_verification_steps()
    compare_versions()
    
    print("\n🎯 关键修复:")
    print("  1. 移除了可能破坏文件的强制重命名")
    print("  2. 添加了Windows可执行文件签名验证")
    print("  3. 简化了构建流程，回到可靠的方式")
    print("  4. 增加了详细的调试信息")
    
    print("\n✅ 推送更新后，GitHub Actions将:")
    print("  - 生成正确的Windows .exe文件")
    print("  - 验证文件完整性和可执行性")
    print("  - 提供详细的构建日志")
    print("  - 确保文件可以正常双击运行")
