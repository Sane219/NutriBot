#!/usr/bin/env python3
"""
Setup checker for NutriBot application
Verifies that all dependencies and components are working correctly
"""

import sys
import os
import importlib
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} - Need Python 3.8+")
        return False

def check_dependencies():
    """Check if all required packages are installed"""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        'streamlit', 'pandas', 'numpy', 'scikit-learn', 
        'PIL', 'easyocr', 'plotly', 'joblib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                importlib.import_module('PIL')
            else:
                importlib.import_module(package)
            print(f"   ✅ {package} - OK")
        except ImportError:
            print(f"   ❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n   Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_project_structure():
    """Check if project structure is correct"""
    print("\n📁 Checking project structure...")
    
    required_dirs = ['app', 'models', 'data', 'data/raw']
    required_files = [
        'app/main.py', 'app/ocr.py', 'app/processor.py',
        'models/diet_classifier.py', 'models/health_score_model.py',
        'requirements.txt'
    ]
    
    all_good = True
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"   ✅ {directory}/ - OK")
        else:
            print(f"   ❌ {directory}/ - MISSING")
            all_good = False
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path} - OK")
        else:
            print(f"   ❌ {file_path} - MISSING")
            all_good = False
    
    return all_good

def check_data_files():
    """Check if data files are available"""
    print("\n📊 Checking data files...")
    
    usda_file = "data/raw/USDA.csv"
    model_files = ["models/health_score_model.pkl", "models/scaler.pkl"]
    
    if os.path.exists(usda_file):
        print(f"   ✅ {usda_file} - OK")
        # Check file size
        size_mb = os.path.getsize(usda_file) / (1024 * 1024)
        print(f"      File size: {size_mb:.1f} MB")
    else:
        print(f"   ⚠️  {usda_file} - MISSING (will use fallback scoring)")
    
    model_available = True
    for model_file in model_files:
        if os.path.exists(model_file):
            print(f"   ✅ {model_file} - OK")
        else:
            print(f"   ⚠️  {model_file} - MISSING (will use fallback scoring)")
            model_available = False
    
    return model_available

def check_imports():
    """Test importing main modules"""
    print("\n🔧 Testing module imports...")
    
    try:
        sys.path.append('app')
        from processor import NutriAnalyzer
        print("   ✅ NutriAnalyzer - OK")
        
        from ocr import OCRProcessor
        print("   ✅ OCRProcessor - OK")
        
        sys.path.append('models')
        from diet_classifier import DietClassifier
        print("   ✅ DietClassifier - OK")
        
        from health_score_model import HealthScoreModel
        print("   ✅ HealthScoreModel - OK")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False

def check_streamlit_compatibility():
    """Check Streamlit version and compatibility"""
    print("\n🌊 Checking Streamlit compatibility...")
    
    try:
        import streamlit as st
        version = st.__version__
        print(f"   ✅ Streamlit {version} - OK")
        
        # Check for known compatibility issues
        major, minor = version.split('.')[:2]
        if int(major) >= 1 and int(minor) >= 28:
            print("   ✅ Version supports modern API - OK")
        else:
            print("   ⚠️  Older version - some features may not work")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Streamlit check failed: {e}")
        return False

def main():
    """Run all checks"""
    print("🔍 NutriBot Setup Checker")
    print("=" * 50)
    
    checks = [
        check_python_version(),
        check_dependencies(),
        check_project_structure(),
        check_imports(),
        check_streamlit_compatibility()
    ]
    
    # Data files are optional
    check_data_files()
    
    print("\n" + "=" * 50)
    
    if all(checks):
        print("🎉 All checks passed! Your setup looks good.")
        print("\n🚀 You can now run the app with:")
        print("   streamlit run app/main.py")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\n📋 Common fixes:")
        print("   • Install missing packages: pip install -r requirements.txt")
        print("   • Check file paths and project structure")
        print("   • Ensure you're in the project root directory")
    
    return all(checks)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)