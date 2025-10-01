#!/usr/bin/env python3
"""
Test script for NHL Card Browser
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import tkinter as tk
        print("✓ tkinter imported")
    except ImportError as e:
        print(f"✗ tkinter import failed: {e}")
        return False
    
    try:
        from PIL import Image, ImageTk
        print("✓ PIL imported")
    except ImportError as e:
        print(f"✗ PIL import failed: {e}")
        return False
    
    try:
        import requests
        print("✓ requests imported")
    except ImportError as e:
        print(f"✗ requests import failed: {e}")
        return False
    
    try:
        import json
        print("✓ json imported")
    except ImportError as e:
        print(f"✗ json import failed: {e}")
        return False
    
    return True

def test_data_loading():
    """Test if data can be loaded"""
    print("\nTesting data loading...")
    
    # Check if data directory exists
    data_dir = Path("data")
    if not data_dir.exists():
        print("✗ Data directory not found")
        return False
    
    # Check for JSON files
    json_files = list(data_dir.glob("*.json"))
    if not json_files:
        print("✗ No JSON files found in data directory")
        return False
    
    print(f"✓ Found {len(json_files)} JSON files")
    
    # Test loading one file
    try:
        import json
        with open(json_files[0], 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✓ Successfully loaded {json_files[0].name}")
        return True
    except Exception as e:
        print(f"✗ Failed to load {json_files[0].name}: {e}")
        return False

def main():
    """Run all tests"""
    print("NHL Card Browser - Test Suite")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Data Loading Test", test_data_loading)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            print(f"✓ {test_name} PASSED")
            passed += 1
        else:
            print(f"✗ {test_name} FAILED")
    
    print(f"\n{'=' * 40}")
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready to run the browser.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the requirements.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)