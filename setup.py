#!/usr/bin/env python3
"""
Setup script for NHL Card Monitor
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="nhl-card-monitor",
    version="1.0.0",
    author="NHL Card Monitor Team",
    author_email="support@example.com",
    description="Automaattinen korttien seuranta NHL HUT Builderille",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/username/nhl-card-monitor",
    project_urls={
        "Bug Reports": "https://github.com/username/nhl-card-monitor/issues",
        "Source": "https://github.com/username/nhl-card-monitor",
        "Documentation": "https://github.com/username/nhl-card-monitor/wiki",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment :: Sports",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "gui": [
            "tkinter",
        ],
        "build": [
            "pyinstaller>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "nhl-monitor=nhl_card_monitor_console:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.md", "*.txt", "*.bat", "*.ps1"],
    },
    keywords="nhl, hockey, cards, monitor, automation, scraping",
    zip_safe=False,
)