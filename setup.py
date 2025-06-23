#!/usr/bin/env python3
"""
Setup script for File Converter Web Application
"""
from setuptools import setup, find_packages

# Read the contents of README file
def read_description():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "Universal File Converter - Supporting 31+ conversion types including PDF, Images, Audio, Video & Documents"

setup(
    name="file-converter-app",
    version="1.0.0",
    author="File Converter Team",
    description="Universal File Converter Web Application",
    long_description=read_description(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.11",
    install_requires=[
        "Flask>=3.0.0",
        "Flask-SQLAlchemy>=3.1.1",
        "gunicorn>=21.2.0",
        "Werkzeug>=3.0.1",
        "psycopg2-binary>=2.9.9",
        "Pillow>=10.1.0",
        "PyMuPDF>=1.23.8",
        "pdfkit>=1.0.0",
        "pdf2docx>=0.5.6",
        "reportlab>=4.0.7",
        "python-docx>=1.1.0",
        "openpyxl>=3.1.2",
        "pandas>=2.1.4",
        "ffmpeg-python>=0.2.0",
        "email-validator>=2.1.0",
    ],
    entry_points={
        "console_scripts": [
            "file-converter=main:app",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["templates/*", "static/*/*", "*.html"],
    },
)