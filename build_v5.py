#!/usr/bin/env python3
"""
Amazon Japan Scraper v5.0 - Build Script
Build script for creating standalone executable using PyInstaller
"""

import subprocess
import sys
import os
import shutil
import platform

def main():
    print('='*70)
    print('Amazon Japan Scraper v5.0 - Build Script')
    print('='*70)
    print()
    
    # Check if main_selenium_only.py exists
    if not os.path.exists('main_selenium_only.py'):
        print('ERROR: main_selenium_only.py not found!')
        sys.exit(1)
    
    print('Building Amazon Japan Scraper v5.0...')
    print()
    
    # Determine executable name based on platform
    is_windows = platform.system() == 'Windows'
    exe_name = 'Amazon_Japan_Scraper_v5.0_Selenium'
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        f'--name={exe_name}',
        '--hidden-import=selenium',
        '--hidden-import=undetected_chromedriver',
        '--hidden-import=pandas',
        '--hidden-import=openpyxl',
        '--hidden-import=beautifulsoup4',
        '--hidden-import=bs4',
        '--hidden-import=lxml',
        '--hidden-import=numpy',
        '--hidden-import=requests',
        '--hidden-import=urllib3',
        '--hidden-import=certifi',
        '--hidden-import=idna',
        '--hidden-import=charset_normalizer',
        '--hidden-import=soupsieve',
        '--hidden-import=et_xmlfile',
        '--hidden-import=dateutil',
        '--hidden-import=pytz',
        '--hidden-import=six',
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--icon=NONE',
        '--noconfirm',
        '--clean',
        'main_selenium_only.py'
    ]
    
    print('PyInstaller command:')
    print(' '.join(cmd))
    print()
    
    # Run PyInstaller
    try:
        if is_windows:
            result = subprocess.run(cmd, check=True, encoding='cp1252', errors='replace')
        else:
            result = subprocess.run(cmd, check=True)
        print('\nBuild successful!')
    except subprocess.CalledProcessError as e:
        print(f'\nERROR: Build failed with exit code {e.returncode}')
        sys.exit(1)
    except Exception as e:
        print(f'\nERROR: {e}')
        sys.exit(1)
    
    # Create release directory
    release_dir = 'release_v5'
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    os.makedirs(release_dir)
    
    print(f'\nCreating release directory: {release_dir}/')
    
    # Copy executable
    dist_dir = 'dist'
    if is_windows:
        exe_file = f'{exe_name}.exe'
    else:
        exe_file = exe_name
    
    src_path = os.path.join(dist_dir, exe_file)
    dst_path = os.path.join(release_dir, exe_file)
    
    if os.path.exists(src_path):
        shutil.copy2(src_path, dst_path)
        print(f'Copied: {exe_file}')
        
        # Verify file size
        size_kb = os.path.getsize(dst_path) / 1024
        print(f'Size: {size_kb:.1f} KB')
        
        # On Windows, verify it's an actual executable
        if is_windows:
            with open(dst_path, 'rb') as f:
                magic = f.read(2)
                if magic == b'MZ':
                    print('Verified: Valid Windows executable (MZ header)')
                else:
                    print('WARNING: File does not have MZ header!')
    else:
        print(f'ERROR: Executable not found at {src_path}')
        sys.exit(1)
    
    # Create README
    readme_content = """Amazon Japan Scraper v5.0 - Selenium Edition
================================================

VERSION HIGHLIGHTS:
- Pure Selenium implementation with undetected-chromedriver
- Bypasses Amazon's anti-bot measures
- Enhanced seller information extraction (phone, address, company name)
- Chinese column names in Excel export
- Real-time data saving
- Stable and reliable product/seller scraping

WHAT'S NEW IN v5.0:
- Complete rewrite using Selenium for better reliability
- 93% seller identification rate
- 73% address extraction rate
- 20% phone number extraction rate (varies by seller)
- Support for both Chinese and Japanese seller information formats
- Automatic handling of different seller page structures

SYSTEM REQUIREMENTS:
- Windows 10/11 (64-bit)
- Internet connection
- Google Chrome browser (will be used in headless mode)

USAGE:
1. Run the executable
2. Enter search keyword (e.g., iPhone case, lipstick, luggage)
3. Set number of pages and products per page
4. Click "Start Search"
5. Results will be saved to amazon_data/ folder as Excel files

EXCEL OUTPUT:
- Two sheets: Product Information and Seller Information
- Chinese column headers for better readability
- All data automatically saved during search

NOTES:
- Some sellers may not publicly display phone numbers (this is normal)
- Seller information completeness varies by seller
- Search speed: approximately 8-10 seconds per product
- Recommended: 1-3 pages per search for optimal performance

For issues or updates, visit:
https://github.com/[your-username]/AmazonJapanScraper
"""
    
    readme_path = os.path.join(release_dir, 'README.txt')
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print('Created: README.txt')
    
    print()
    print('='*70)
    print('Build Complete!')
    print('='*70)
    print(f'Release files are in: {release_dir}/')
    print()

if __name__ == '__main__':
    main()

