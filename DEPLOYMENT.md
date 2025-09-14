# 🚀 部署指南

本指南将帮助您将Amazon Japan Scraper部署到GitHub并设置自动化构建。

## 📋 准备工作

### 1. 创建GitHub仓库

1. 登录GitHub，创建新仓库
2. 仓库名建议：`amazon-japan-scraper`
3. 设置为Public（如果要使用GitHub Actions免费额度）
4. 不要初始化README（我们已经有了）

### 2. 本地Git配置

```bash
# 在项目目录中初始化Git
git init

# 添加所有文件
git add .

# 提交初始版本
git commit -m "Initial commit: Amazon Japan Scraper v2.0 with multilingual support"

# 添加远程仓库（替换为您的仓库URL）
git remote add origin https://github.com/YOUR_USERNAME/amazon-japan-scraper.git

# 推送到GitHub
git branch -M main
git push -u origin main
```

## 🔧 GitHub Actions设置

### 自动触发构建

GitHub Actions已配置为在以下情况自动构建：

1. **推送代码**到main分支
2. **创建Pull Request**
3. **创建标签**（用于发布）
4. **手动触发**

### 创建发布版本

```bash
# 创建并推送标签
git tag v2.0.0
git push origin v2.0.0
```

这将自动触发：
- Windows可执行文件构建
- 安装程序创建
- GitHub Release发布

## 📦 本地构建测试

### Windows环境

```bash
# 安装依赖和构建工具
./install_and_build.bat

# 或手动执行
pip install -r requirements.txt
pip install pyinstaller
python build_windows.py
```

### 验证构建结果

构建成功后，检查以下文件：
- `release/Amazon_Japan_Scraper_v2.0.exe`
- `release/README.txt`

## 🌐 发布流程

### 1. 准备发布

1. 更新版本号（在多个文件中）：
   - `setup.py`
   - `pyproject.toml`
   - `build_windows.py`
   - `main.py`（GUI标题）

2. 更新CHANGELOG或README

3. 测试功能确保正常工作

### 2. 创建发布

```bash
# 提交所有更改
git add .
git commit -m "Prepare release v2.0.0"
git push

# 创建标签
git tag v2.0.0
git push origin v2.0.0
```

### 3. 验证发布

1. 检查GitHub Actions是否成功运行
2. 验证Release页面是否创建
3. 下载并测试生成的可执行文件

## 🔍 故障排除

### GitHub Actions失败

1. **依赖安装失败**
   - 检查`requirements.txt`格式
   - 确认包名和版本号正确

2. **构建失败**
   - 查看Actions日志
   - 检查Python版本兼容性
   - 验证PyInstaller配置

3. **发布失败**
   - 确认有GITHUB_TOKEN权限
   - 检查标签格式（必须以v开头）

### 本地构建问题

1. **Python版本**
   ```bash
   python --version  # 应该是3.9+
   ```

2. **依赖冲突**
   ```bash
   # 创建虚拟环境
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

3. **PyInstaller问题**
   ```bash
   # 清理缓存
   pyinstaller --clean amazon_scraper.spec
   ```

## 📊 监控和维护

### 定期检查

1. **依赖更新**
   ```bash
   pip list --outdated
   pip install --upgrade package_name
   ```

2. **安全漏洞**
   ```bash
   pip audit  # 如果可用
   ```

3. **功能测试**
   - 定期测试主要功能
   - 检查Amazon页面结构变化

### 版本管理

使用语义化版本控制：
- `MAJOR.MINOR.PATCH`
- 主要功能：MAJOR
- 新功能：MINOR  
- 修复：PATCH

## 🎯 最佳实践

### 代码质量

1. **代码格式化**
   ```bash
   pip install black
   black main.py
   ```

2. **代码检查**
   ```bash
   pip install flake8
   flake8 main.py
   ```

### 安全考虑

1. **不要提交敏感信息**
   - API密钥
   - 个人数据
   - 测试数据

2. **使用环境变量**
   ```python
   import os
   api_key = os.getenv('API_KEY')
   ```

### 用户体验

1. **清晰的错误消息**
2. **详细的使用说明**
3. **及时的功能更新**

## 📞 支持

如果遇到部署问题：

1. 检查本文档的故障排除部分
2. 查看GitHub Issues
3. 创建新的Issue描述问题

---

**注意**: 请确保遵守所有相关的使用条款和法律法规。
