# 🛒 Amazon Japan 卖家信息提取工具 v2.0

[![Build Windows Executable](https://github.com/your-username/amazon-japan-scraper/actions/workflows/build-windows.yml/badge.svg)](https://github.com/your-username/amazon-japan-scraper/actions/workflows/build-windows.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

一个功能强大的Amazon日本站卖家信息提取工具，支持多语言卖家信息提取和现代化用户界面。

## ✨ 功能特点

### 🌍 多语言支持
- **中文拼音格式**: `ZhouKouHuiLingShangMaoYouXianGongSi`
- **英文格式**: `Shenzhen Chuanzheng Technology CO.,Ltd`
- **日文格式**: `株式会社ユニーク`
- **韩文格式**: `AMOREPACIFIC JAPAN Co.,Ltd`

### 📊 详细信息提取
- 🏢 **Business Name**: 公司名称
- 📞 **咨询用电话号码**: 联系电话
- 📍 **地址**: 详细地址信息
- 👤 **购物代表姓名**: 联系人姓名
- 🏪 **商店名**: 店铺名称

### 🎨 现代化界面
- 美观的用户界面设计
- 实时搜索进度显示
- 智能重复卖家过滤
- 多格式数据导出（Excel/CSV）

## 🚀 快速开始

### 方式一：下载可执行文件（推荐）

1. 前往 [Releases](https://github.com/your-username/amazon-japan-scraper/releases) 页面
2. 下载最新版本的 `Amazon_Japan_Scraper_v2.0.exe`
3. 双击运行，无需安装

### 方式二：从源码运行

```bash
# 克隆仓库
git clone https://github.com/your-username/amazon-japan-scraper.git
cd amazon-japan-scraper

# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

## 📋 使用说明

### 基本操作

1. **选择搜索方式**
   - 选择预定义商品类目
   - 或输入自定义日文关键词

2. **设置搜索参数**
   - 搜索页数：1-10页
   - 最大产品数：10-500个

3. **开始搜索**
   - 点击"🚀 开始搜索"按钮
   - 实时查看搜索进度

4. **导出结果**
   - 搜索完成后点击"📊 导出数据"
   - 支持Excel和CSV格式

### 高级功能

- **智能去重**: 自动过滤重复卖家
- **多语言识别**: 自动识别不同语言格式的卖家信息
- **实时统计**: 显示提取成功率和质量统计

## 🛠️ 开发环境

### 系统要求
- Python 3.9+
- Windows 10+ (用于构建Windows可执行文件)

### 依赖包
```
requests>=2.28.0
beautifulsoup4>=4.11.0
pandas>=1.5.0
openpyxl>=3.0.0
lxml>=4.9.0
```

### 构建Windows可执行文件

```bash
# 安装构建依赖
pip install pyinstaller

# 运行构建脚本
python build_windows.py
```

## 🔧 GitHub Actions 自动化

本项目配置了GitHub Actions自动化构建流程：

- **自动构建**: 每次推送代码时自动构建Windows可执行文件
- **自动发布**: 创建标签时自动发布新版本
- **多格式输出**: 同时生成可执行文件和安装程序

### 触发构建

```bash
# 创建新版本标签
git tag v2.0.0
git push origin v2.0.0
```

## 📊 提取效果统计

基于最新测试结果：

| 字段类型 | 提取成功率 | 支持语言 |
|----------|------------|----------|
| Business Name | 50% | 中英日韩 |
| 咨询用电话号码 | 32% | 国际格式 |
| 购物代表姓名 | 50% | 中英日韩 |
| 商店名 | 50% | 中英日韩 |
| 地址 | 3% | 中英日 |

## ⚠️ 注意事项

1. **合规使用**
   - 请遵守Amazon的使用条款
   - 避免频繁请求，建议设置适当延迟
   - 数据仅供学习和研究使用

2. **技术限制**
   - 依赖网络连接
   - 可能受到网站反爬虫机制影响
   - 提取效果可能因页面结构变化而变化

3. **隐私保护**
   - 不存储用户个人信息
   - 所有数据仅在本地处理

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 更新日志

### v2.0.0 (2024-09-13)
- 🆕 多语言卖家信息提取支持
- 🎨 全新现代化用户界面
- 🔄 智能重复卖家过滤
- 📊 增强的数据提取能力
- 🚀 GitHub Actions自动化构建

### v1.0.0
- 基础产品搜索功能
- 简单卖家信息提取
- 数据导出功能

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。

## 🙏 致谢

- [Requests](https://requests.readthedocs.io/) - HTTP库
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - HTML解析
- [Pandas](https://pandas.pydata.org/) - 数据处理
- [Tkinter](https://docs.python.org/3/library/tkinter.html) - GUI框架

---

**免责声明**: 本工具仅供学习和研究使用，请遵守相关网站的使用条款和法律法规。
