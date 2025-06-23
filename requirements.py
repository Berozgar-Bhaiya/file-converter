#!/usr/bin/env python3
"""
Requirements installer script for File Converter Web Application
This script installs all necessary Python packages for the file conversion system.
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a single package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ Failed to install {package}")
        return False

def main():
    """Main function to install all required packages"""
    print("File Converter - Installing Python Requirements")
    print("=" * 50)
    
    # List of required packages with compatible versions
    packages = [
        # Core web framework
        "Flask>=3.0.0",
        "Flask-SQLAlchemy>=3.1.1", 
        "Werkzeug>=3.0.1",
        "gunicorn>=21.2.0",
        
        # Database
        "psycopg2-binary>=2.9.9",
        
        # Image processing
        "Pillow>=10.1.0",
        
        # PDF processing
        "PyMuPDF>=1.23.8",
        "pdfkit>=1.0.0",
        "pdf2docx>=0.5.6",
        "reportlab>=4.0.7",
        
        # Document processing
        "python-docx>=1.1.0",
        "openpyxl>=3.1.2",
        "pandas>=2.1.4",
        
        # Audio/Video processing
        "ffmpeg-python>=0.2.0",
        
        # Email validation
        "email-validator>=2.1.0",
    ]
    
    # Install packages
    success_count = 0
    total_packages = len(packages)
    
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"Installation Summary:")
    print(f"Successfully installed: {success_count}/{total_packages} packages")
    
    if success_count == total_packages:
        print("✓ All packages installed successfully!")
        print("\nNext steps:")
        print("1. Ensure system dependencies are installed (wkhtmltopdf, ffmpeg)")
        print("2. Set up environment variables if needed")
        print("3. Run: python main.py or gunicorn main:app")
    else:
        print("⚠ Some packages failed to install. Check the output above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())