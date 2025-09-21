#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Amazon Japan Scraper - Ultimate Version Build Script (Safe)
Build Ultimate v4.0 - Encoding Safe Version
"""

import os
import sys
import subprocess
import shutil

def clean_dirs():
    """Clean build directories"""
    for dir_name in ['build', 'dist', 'release_ultimate']:
        if os.path.exists(dir_name):
            print(f"Cleaning: {dir_name}")
            shutil.rmtree(dir_name)

def build_ultimate():
    """Build ultimate version executable"""
    print("Amazon Japan Scraper - Ultimate Version v4.0 Build")
    print("=" * 60)
    clean_dirs()
    
    # Check main file
    if not os.path.exists('main_ultimate.py'):
        print("ERROR: main_ultimate.py not found")
        return False
    
    # Build command - cross-platform compatible
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
        '--hidden-import=numpy',
        '--hidden-import=openpyxl',
        '--hidden-import=concurrent.futures',
        '--hidden-import=urllib3',
        '--hidden-import=certifi',
        '--exclude-module=matplotlib',
        '--exclude-module=scipy',
        '--clean',
        '--noconfirm',
        'main_ultimate.py'
    ]
    
    print("Building Ultimate v4.0...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        # Use safe encoding settings for Windows
        if sys.platform == 'win32':
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, 
                                  encoding='cp1252', errors='replace')
        else:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, 
                                  encoding='utf-8', errors='replace')
        print("Build successful!")
        
        # Check results - cross-platform compatible
        if sys.platform == 'win32':
            exe_name = 'Amazon_Japan_Scraper_v4.0_Ultimate.exe'
        else:
            exe_name = 'Amazon_Japan_Scraper_v4.0_Ultimate'
        
        exe_path = f'dist/{exe_name}'
        
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"Executable created: {exe_path}")
            print(f"Size: {size_mb:.1f} MB")
            
            # Verify file type (Windows only)
            if sys.platform == 'win32':
                try:
                    with open(exe_path, 'rb') as f:
                        header = f.read(2)
                        if header == b'MZ':
                            print("Valid Windows executable (MZ header found)")
                        else:
                            print("Warning: File may not be a valid Windows executable")
                except Exception as e:
                    print(f"Could not verify file header: {e}")
            
            # Create release directory
            os.makedirs('release_ultimate', exist_ok=True)
            
            # Copy file, ensure Windows version has .exe extension
            if sys.platform == 'win32':
                release_name = 'Amazon_Japan_Scraper_v4.0_Ultimate.exe'
            else:
                release_name = 'Amazon_Japan_Scraper_v4.0_Ultimate'
            
            shutil.copy2(exe_path, f'release_ultimate/{release_name}')
            print(f"Copied to release directory: release_ultimate/{release_name}")
            
            # Create README file with safe encoding
            readme_content = """# Amazon Japan Scraper v4.0 - Ultimate Version

## v4.0 Ultimate Features

### Core Improvements
- Expanded keyword search range, supports more small products
- Unlimited continuous search, search as long as you want
- Real-time save function, search and save at the same time
- Four-layer intelligent seller information extraction algorithm
- Support background running, can leave the desktop

### Search Capability Enhancement
- Support any product keywords: phone cases, data cables, small products, etc.
- Multiple search strategies: default, category, brand, price range
- Intelligent deduplication, avoid duplicate data
- Extended product selectors, covering more product types

### Data Management
- Auto-save every 50 products
- Generate both Excel and CSV formats
- Data saved in amazon_data folder
- Support breakpoint resume, not afraid of accidental interruption

### Seller Information Extraction Algorithm
1. **Intelligent keyword extraction** - Based on context analysis
2. **HTML structure extraction** - Using page structure
3. **Regular expression extraction** - Precise pattern matching
4. **Deep text analysis** - Complex text processing

### Extraction Fields
- Company Name (Business Name)
- Phone Number
- Detailed Address (including postal code)
- Representative Name
- Store Name
- Email Address
- Fax Number

### Usage
1. Start the program
2. Enter any product keywords
3. Click "Start Unlimited Search"
4. Can minimize window, run in background
5. Data automatically saved, can stop at any time

### Performance Features
- Intelligent delay control, avoid being blocked
- Concurrent processing, improve efficiency
- Memory optimization, stable long-term operation
- Real-time progress display

### Output Files
- Product information: including title, price, rating, etc.
- Seller information: including complete contact information
- Automatically generated timestamp file names

Version: 4.0.0 - Ultimate Version
Build Time: 2024
"""
            
            try:
                with open('release_ultimate/README.txt', 'w', encoding='utf-8') as f:
                    f.write(readme_content)
            except Exception as e:
                # Fallback to ASCII if UTF-8 fails
                with open('release_ultimate/README.txt', 'w', encoding='ascii', errors='replace') as f:
                    f.write(readme_content)
            
            print("Release package created in 'release_ultimate' directory")
            return True
        else:
            print("ERROR: Executable not found after build")
            return False
    except subprocess.CalledProcessError as e:
        error_msg = "Build failed"
        if e.stderr:
            try:
                error_msg = str(e.stderr)
            except:
                error_msg = "Build failed with encoding error"
        print(f"Build error: {error_msg}")
        return False
    except Exception as e:
        try:
            error_msg = str(e)
        except:
            error_msg = "Unknown error occurred"
        print(f"An unexpected error occurred: {error_msg}")
        return False

if __name__ == "__main__":
    if not build_ultimate():
        sys.exit(1)
