# Amazon Japan Scraper v5.0 - Selenium Edition

[![Build Amazon Japan Scraper v5.0](https://github.com/[your-username]/AmazonJapanScraper/actions/workflows/build-windows.yml/badge.svg)](https://github.com/[your-username]/AmazonJapanScraper/actions/workflows/build-windows.yml)

🚀 **Professional Amazon Japan product and seller information scraper using Selenium**

## 🎉 v5.0 Major Upgrade - Pure Selenium Implementation

### Key Improvements
- 🌐 **Full Selenium-based** - Uses undetected-chromedriver to bypass anti-bot
- 🎯 **93% seller identification rate** - Significantly improved data extraction
- 📞 **Enhanced phone extraction** - Supports Chinese and Japanese phone formats
- 🏢 **Complete seller info** - Company name, address, phone, email, etc.
- 🇨🇳 **Chinese column names** - Excel headers in Chinese
- 💪 **Stable & Reliable** - Successfully bypasses Amazon's anti-scraping measures

### 📊 Test Results (Based on 15 products)
- **Seller Identification Rate**: 93% (14/15)
- **Address Extraction Rate**: 73% (11/15)
- **Phone Extraction Rate**: 20% (3/15) - Depends on seller disclosure
- **Company Name Rate**: 93% (14/15)
- **Average Speed**: 8-10 seconds per product

## 🆚 Version Comparison

| Feature | v4.0 Ultimate | v5.0 Selenium | Improvement |
|---------|---------------|---------------|-------------|
| Core Tech | HTTP + requests | Selenium + undetected-chromedriver | **Bypass anti-bot** |
| Seller ID Rate | ~60% | 93% | **+55%** |
| Address Rate | ~40% | 73% | **+83%** |
| Phone Rate | ~5% | 20% | **+300%** |
| Stability | Frequent 503 errors | Stable | **Solved** |
| Search Success | ~30% | ~95% | **+217%** |

## 🚀 Features

### Product Information Extraction
- Product title, price, rating
- ASIN and product URL
- Real-time search and extraction

### Seller Information Extraction
- Seller name and store name
- Company name (Business Name)
- Phone number (supports multiple formats)
- Complete address
- Email and fax (if available)
- Representative name (if available)

### Technical Features
- **True Browser Technology**: Uses real Chrome browser for human-like behavior
- **Anti-bot Bypass**: undetected-chromedriver with 95%+ success rate
- **Real-time Saving**: Saves data during search to prevent loss
- **Smart Extraction**: 4-layer extraction algorithm for various page structures
- **Chinese Friendly**: All Excel column names in Chinese
- **Multi-format Support**: Chinese and Japanese phone number formats

## 📦 Installation

### For Users (Windows)
1. Download the latest release: `Amazon_Japan_Scraper_v5.0_Selenium.exe`
2. Double-click to run (no installation needed)
3. Google Chrome browser required (program uses headless mode)

### For Developers
```bash
git clone https://github.com/[your-username]/AmazonJapanScraper.git
cd AmazonJapanScraper
pip install -r requirements.txt
python main_selenium_only.py
```

## 🎯 Usage

1. Launch the program (first run will download ChromeDriver)
2. Enter search keyword (e.g., "iPhone case", "lipstick", "luggage")
3. Set number of pages and products per page
4. Click "Start Search"
5. Results automatically saved to `amazon_data/` folder

### Recommended Settings
- **Quick Test**: 1 page, 10 products (~1-2 minutes)
- **Medium Scale**: 3 pages, 30 products (~5-8 minutes)
- **Large Scale**: 5-10 pages, 50-100 products (~15-30 minutes)

## 📊 Data Output

### Excel File Structure
Two sheets with Chinese headers:

**Sheet 1: Product Information (产品信息)**
- Product Title (产品标题)
- Price (价格)
- Rating (评分)
- Product URL (产品链接)
- ASIN (产品ASIN)

**Sheet 2: Seller Information (卖家信息)**
- Seller Name (卖家名称)
- Company Name (公司名称)
- Phone Number (电话号码)
- Address (地址)
- Email (电子邮箱)
- Associated Product (关联产品)

## 🛡️ Stability Guarantees

- Intelligent delay control to avoid blocking
- Session management for long-term stable operation
- Automatic error recovery - individual failures don't affect overall process
- Automatic memory cleanup - no overflow issues

## ⚙️ System Requirements

- **OS**: Windows 10/11 (64-bit)
- **Browser**: Google Chrome (latest version)
- **Internet**: Stable connection required
- **RAM**: 4GB+ recommended
- **Disk**: 100MB+ free space

## 💡 Tips

- Limit to 100 products per search for optimal performance
- Phone extraction rate varies (20% is normal) due to seller privacy settings
- For large datasets, run in multiple batches
- Best results with stable internet connection

## 🔧 Building from Source

```bash
# Install build dependencies
pip install pyinstaller

# Build executable
python build_v5.py

# Output will be in release_v5/ directory
```

## ⚠️ Important Notes

- First run downloads ChromeDriver (~10-20MB)
- Program uses headless Chrome - no visible browser window
- Please use responsibly and follow Amazon's Terms of Service
- Data for educational and research purposes only
- Not all sellers publicly display phone numbers (this is normal)

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues or feature requests, please open an issue on GitHub.

---

**Made with ❤️ for Amazon Japan sellers research**

**Version**: 5.0.0 - Selenium Edition  
**Last Updated**: October 2025
