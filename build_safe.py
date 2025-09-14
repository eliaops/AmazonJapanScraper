"""
Safe Windows build script - avoids all encoding issues
"""

import os
import sys
import subprocess
import shutil

def main():
    print("Amazon Japan Scraper - Windows Build")
    print("=" * 50)
    
    # Clean previous builds
    for dirname in ['build', 'dist', '__pycache__', 'release']:
        if os.path.exists(dirname):
            print(f"Cleaning: {dirname}")
            shutil.rmtree(dirname)
    
    # Check main file
    if not os.path.exists('main.py'):
        print("ERROR: main.py not found")
        return False
    
    # Build command - use full path for pyinstaller
    pyinstaller_path = '/Users/evan/Library/Python/3.9/bin/pyinstaller'
    if not os.path.exists(pyinstaller_path):
        pyinstaller_path = 'pyinstaller'  # fallback to PATH
    
    cmd = [
        pyinstaller_path,
        '--onefile',
        '--windowed', 
        '--name=Amazon_Japan_Scraper_v2.0',
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=requests',
        '--hidden-import=bs4',
        '--hidden-import=pandas',
        '--hidden-import=openpyxl',
        '--exclude-module=matplotlib',
        '--exclude-module=scipy',
        '--clean',
        'main.py'
    ]
    
    print("Building executable...")
    print("Command:", ' '.join(cmd))
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        
        # Check result - different extensions for different platforms
        exe_name = 'Amazon_Japan_Scraper_v2.0.exe' if sys.platform == 'win32' else 'Amazon_Japan_Scraper_v2.0'
        exe_path = f'dist/{exe_name}'
        
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"Executable created: {exe_path}")
            print(f"Size: {size_mb:.1f} MB")
            
            # Create release directory
            os.makedirs('release', exist_ok=True)
            release_name = 'Amazon_Japan_Scraper_v2.0.exe' if sys.platform == 'win32' else 'Amazon_Japan_Scraper_v2.0'
            shutil.copy2(exe_path, f'release/{release_name}')
            
            # Create simple readme
            with open('release/README.txt', 'w') as f:
                f.write("Amazon Japan Scraper v2.0\n")
                f.write("Double-click the exe file to run.\n")
                f.write("Requires Windows 10 or later.\n")
            
            print("Release package created in 'release' directory")
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
