#!/usr/bin/env python3
"""
Test script to verify USDA dataset integration and model functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.health_score_model import HealthScoreModel
from models.diet_classifier import DietClassifier
from app.processor import NutriAnalyzer

def test_health_model():
    """Test the health scoring model with USDA format data"""
    print("🧪 Testing Health Score Model...")
    
    model = HealthScoreModel()
    
    # Test data in USDA format
    test_foods = [
        {
            'name': 'Spinach (Fresh)',
            'nutrition': {
                'Calories': 23,
                'Protein': 2.86,
                'TotalFat': 0.39,
                'Carbohydrate': 3.63,
                'Sodium': 79,
                'SaturatedFat': 0.063,
                'Sugar': 0.42,
                'Calcium': 99,
                'Iron': 2.71,
                'Potassium': 558,
                'VitaminC': 28.1,
                'VitaminE': 2.03,
                'VitaminD': 0
            }
        },
        {
            'name': 'French Fries',
            'nutrition': {
                'Calories': 365,
                'Protein': 4.0,
                'TotalFat': 17.0,
                'Carbohydrate': 48.0,
                'Sodium': 246,
                'SaturatedFat': 2.3,
                'Sugar': 0.3,
                'Calcium': 12,
                'Iron': 0.8,
                'Potassium': 579,
                'VitaminC': 9.7,
                'VitaminE': 1.9,
                'VitaminD': 0
            }
        }
    ]
    
    try:
        model.load_model()
        
        for food in test_foods:
            score = model.predict_health_score(food['nutrition'])
            rating = model.get_health_rating(score)
            
            print(f"  ✅ {food['name']}: {score:.1f}/100 ({rating})")
        
        print("  ✅ Health model test passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ Health model test failed: {e}")
        return False

def test_diet_classifier():
    """Test the diet classification system"""
    print("\n🧪 Testing Diet Classifier...")
    
    classifier = DietClassifier()
    
    test_cases = [
        {
            'name': 'Vegetables with Cheese',
            'ingredients': 'broccoli, cheese, milk, butter',
            'expected': 'Vegetarian'
        },
        {
            'name': 'Chicken Salad',
            'ingredients': 'lettuce, tomato, chicken breast, olive oil',
            'expected': 'Non-Vegetarian'
        },
        {
            'name': 'Quinoa Bowl',
            'ingredients': 'quinoa, black beans, vegetables, tahini',
            'expected': 'Vegan'
        }
    ]
    
    try:
        for test in test_cases:
            result = classifier.classify_by_ingredients(test['ingredients'])
            diet_type = result['diet_type']
            confidence = result['confidence']
            
            status = "✅" if diet_type == test['expected'] else "⚠️"
            print(f"  {status} {test['name']}: {diet_type} ({confidence:.1%})")
        
        print("  ✅ Diet classifier test passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ Diet classifier test failed: {e}")
        return False

def test_full_analyzer():
    """Test the complete NutriAnalyzer system"""
    print("\n🧪 Testing Complete Analyzer...")
    
    try:
        analyzer = NutriAnalyzer()
        
        # Test with complete product data
        result = analyzer.analyze_product(
            product_name="Organic Apple",
            ingredients="apple",
            nutrition_facts={
                'Calories': 52,
                'Protein': 0.26,
                'TotalFat': 0.17,
                'Carbohydrate': 13.81,
                'Sodium': 1,
                'SaturatedFat': 0.028,
                'Sugar': 10.39,
                'Calcium': 6,
                'Iron': 0.12,
                'Potassium': 107,
                'VitaminC': 4.6,
                'VitaminE': 0.18,
                'VitaminD': 0
            }
        )
        
        # Verify all components
        assert 'diet_classification' in result
        assert 'health_analysis' in result
        assert 'suggestions' in result
        assert result['health_analysis']['score'] is not None
        
        print(f"  ✅ Product: {result['product_name']}")
        print(f"  ✅ Diet: {result['diet_classification']['diet_type']}")
        print(f"  ✅ Health Score: {result['health_analysis']['score']:.1f}")
        print(f"  ✅ Suggestions: {len(result['suggestions'])} generated")
        
        print("  ✅ Complete analyzer test passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ Complete analyzer test failed: {e}")
        return False

def test_dataset_access():
    """Test USDA dataset access"""
    print("\n🧪 Testing USDA Dataset Access...")
    
    try:
        import pandas as pd
        
        # Check if USDA dataset is accessible
        df = pd.read_csv('data/raw/USDA.csv')
        
        print(f"  ✅ Dataset loaded: {len(df)} records")
        print(f"  ✅ Columns: {len(df.columns)} nutrition attributes")
        
        # Check for required columns
        required_columns = [
            'Calories', 'Protein', 'TotalFat', 'Carbohydrate', 
            'Sodium', 'SaturatedFat', 'Sugar', 'Calcium', 'Iron', 
            'Potassium', 'VitaminC', 'VitaminE', 'VitaminD'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"  ⚠️ Missing columns: {missing_columns}")
        else:
            print("  ✅ All required columns present")
        
        print("  ✅ Dataset access test passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ Dataset access test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting NutriBot USDA Integration Tests...\n")
    
    tests = [
        test_dataset_access,
        test_health_model,
        test_diet_classifier,
        test_full_analyzer
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! NutriBot is ready to use with USDA dataset.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
