#!/usr/bin/env python3
"""
Test script to verify OCR functionality
"""

import sys
import os
sys.path.append('app')

def test_ocr_basic():
    """Test basic OCR functionality"""
    print("🔍 Testing OCR functionality...")
    
    try:
        from ocr import OCRProcessor
        print("   ✅ OCR module imported successfully")
        
        # Test with sample text
        ocr = OCRProcessor()
        print("   ✅ OCR processor initialized")
        
        # Test text parsing
        sample_text = """
        Healthy Granola Bar
        
        Ingredients: Oats, honey, almonds, dried cranberries, coconut oil
        
        Nutrition Facts per 100g:
        Calories: 450
        Total Fat: 18g
        Saturated Fat: 6g
        Sugars: 25g
        Fiber: 8g
        Protein: 12g
        Sodium: 150mg
        """
        
        parsed = ocr._parse_extracted_text(sample_text)
        print("   ✅ Text parsing works")
        print(f"      Product Name: '{parsed.get('product_name', 'None')}'")
        print(f"      Ingredients: '{parsed.get('ingredients', 'None')[:50]}...'")
        print(f"      Nutrition: '{parsed.get('nutrition_facts', 'None')[:50]}...'")
        
        # Test nutrition extraction
        nutrition = ocr.extract_nutrition_values(sample_text)
        print("   ✅ Nutrition extraction works")
        print(f"      Found {len(nutrition)} nutrition values")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ OCR test failed: {e}")
        return False

def test_empty_text():
    """Test OCR with empty or minimal text"""
    print("\n🔍 Testing OCR with edge cases...")
    
    try:
        from ocr import OCRProcessor
        ocr = OCRProcessor()
        
        # Test with empty text
        result = ocr._parse_extracted_text("")
        print(f"   ✅ Empty text handled: {result}")
        
        # Test with minimal text
        result = ocr._parse_extracted_text("Snack Bar")
        print(f"   ✅ Minimal text handled: {result}")
        
        # Test with just numbers
        result = ocr._parse_extracted_text("450 18 6 25")
        print(f"   ✅ Numbers only handled: {result}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Edge case test failed: {e}")
        return False

def test_processor_integration():
    """Test integration with NutriAnalyzer"""
    print("\n🔍 Testing processor integration...")
    
    try:
        from processor import NutriAnalyzer
        analyzer = NutriAnalyzer()
        print("   ✅ NutriAnalyzer initialized")
        
        # Test with minimal data
        result = analyzer.analyze_product(
            product_name="Test Snack",
            ingredients="",
            nutrition_facts={}
        )
        
        print("   ✅ Analysis with minimal data works")
        print(f"      Diet type: {result['diet_classification']['diet_type']}")
        print(f"      Health score: {result['health_analysis'].get('score', 'None')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Processor integration test failed: {e}")
        return False

def main():
    """Run all OCR tests"""
    print("🧪 OCR Functionality Tests")
    print("=" * 50)
    
    tests = [
        test_ocr_basic(),
        test_empty_text(),
        test_processor_integration()
    ]
    
    print("\n" + "=" * 50)
    
    if all(tests):
        print("🎉 All OCR tests passed!")
        print("\n💡 If you're still seeing issues:")
        print("   • Make sure EasyOCR is installed: pip install easyocr")
        print("   • Try uploading a clearer image with visible text")
        print("   • Enable debug mode to see what text is being extracted")
    else:
        print("❌ Some OCR tests failed.")
        print("\n🔧 Try these fixes:")
        print("   • Install missing dependencies: pip install -r requirements.txt")
        print("   • Check that EasyOCR is working: python -c 'import easyocr; print(\"OK\")'")
    
    return all(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)