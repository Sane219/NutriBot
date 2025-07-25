import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.health_score_model import HealthScoreModel
from models.diet_classifier import DietClassifier

class NutriAnalyzer:
    """
    Main processor that orchestrates the complete nutrition analysis workflow
    """
    
    def __init__(self):
        self.health_model = HealthScoreModel()
        self.diet_classifier = DietClassifier()
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained models"""
        try:
            self.health_model.load_model()
            print("Health score model loaded successfully")
        except Exception as e:
            print(f"Warning: Could not load health model: {e}")
    
    def analyze_product(self, 
                       product_name: str = "",
                       ingredients: str = "",
                       nutrition_facts: Dict[str, float] = None) -> Dict:
        """
        Complete analysis of a food product
        
        Args:
            product_name: Name of the product
            ingredients: Ingredients list
            nutrition_facts: Dictionary with nutrition values per 100g
            
        Returns:
            Complete analysis results
        """
        results = {
            'product_name': product_name,
            'analysis_status': 'success'
        }
        
        # Diet classification
        try:
            diet_result = self.diet_classifier.classify_by_product_info(
                product_name=product_name,
                ingredients=ingredients
            )
            results['diet_classification'] = diet_result
        except Exception as e:
            results['diet_classification'] = {
                'diet_type': 'Unknown',
                'confidence': 0.0,
                'reason': f'Classification error: {str(e)}'
            }
        
        # Health score prediction
        if nutrition_facts and self.health_model.is_trained:
            try:
                # Ensure all required features are present
                required_features = self.health_model.feature_columns
                complete_nutrition = self._complete_nutrition_data(nutrition_facts)
                
                health_score = self.health_model.predict_health_score(complete_nutrition)
                health_rating = self.health_model.get_health_rating(health_score)
                
                results['health_analysis'] = {
                    'score': float(health_score),
                    'rating': health_rating,
                    'nutrition_data': complete_nutrition
                }
            except Exception as e:
                results['health_analysis'] = {
                    'score': None,
                    'rating': 'Unknown',
                    'error': str(e)
                }
        else:
            results['health_analysis'] = {
                'score': None,
                'rating': 'Insufficient data',
                'nutrition_data': nutrition_facts or {}
            }
        
        # Generate suggestions
        results['suggestions'] = self._generate_suggestions(results)
        
        return results
    
    def _complete_nutrition_data(self, nutrition_facts: Dict[str, float]) -> Dict[str, float]:
        """
        Complete missing nutrition data with reasonable defaults (USDA format)
        """
        defaults = {
            'Calories': 200,  # Reasonable default calories
            'Protein': 8,
            'TotalFat': 5,
            'Carbohydrate': 25,
            'Sodium': 300,  # mg
            'SaturatedFat': 2,
            'Sugar': 5,
            'Calcium': 50,
            'Iron': 2,
            'Potassium': 200,
            'VitaminC': 5,
            'VitaminE': 1,
            'VitaminD': 0
        }
        
        complete_data = defaults.copy()
        complete_data.update(nutrition_facts)
        
        return complete_data
    
    def _generate_suggestions(self, analysis_results: Dict) -> List[str]:
        """
        Generate personalized dietary suggestions based on analysis
        """
        suggestions = []
        
        diet_type = analysis_results.get('diet_classification', {}).get('diet_type', 'Unknown')
        health_analysis = analysis_results.get('health_analysis', {})
        score = health_analysis.get('score')
        nutrition_data = health_analysis.get('nutrition_data', {})
        
        # Diet-specific suggestions
        if diet_type == 'Vegan':
            suggestions.append("🌱 Great choice for plant-based eating!")
            suggestions.append("💪 Consider pairing with protein-rich legumes or nuts")
        elif diet_type == 'Vegetarian':
            suggestions.append("🥛 Contains dairy/eggs - good source of complete proteins")
            suggestions.append("🥬 Add more vegetables for balanced nutrition")
        elif diet_type == 'Non-Vegetarian':
            suggestions.append("🥩 Contains animal products - ensure portion control")
            suggestions.append("🌿 Balance with plant-based sides for fiber")
        
        # Health score-based suggestions
        if score is not None:
            if score >= 80:
                suggestions.append("⭐ Excellent nutritional profile!")
            elif score >= 65:
                suggestions.append("👍 Good nutritional choice")
            elif score >= 45:
                suggestions.append("⚠️ Moderate nutrition - consume in moderation")
            else:
                suggestions.append("❌ Consider healthier alternatives")
        
        # Specific nutrient suggestions
        if nutrition_data:
            # High sugar warning
            if nutrition_data.get('Sugar', 0) > 15:
                suggestions.append("🍯 High in sugar - limit portion size")
            
            # High sodium warning
            if nutrition_data.get('Sodium', 0) > 500:
                suggestions.append("🧂 High sodium content - drink plenty of water")
            
            # High saturated fat warning
            if nutrition_data.get('SaturatedFat', 0) > 5:
                suggestions.append("🧈 High saturated fat - choose lean alternatives")
            
            # Good protein source
            if nutrition_data.get('Protein', 0) > 15:
                suggestions.append("💪 Good protein source!")
            
            # High vitamin C content
            if nutrition_data.get('VitaminC', 0) > 30:
                suggestions.append("🍊 Rich in Vitamin C - great for immunity!")
            
            # Good calcium source
            if nutrition_data.get('Calcium', 0) > 150:
                suggestions.append("🦴 Good source of calcium for bone health!")
        
        return suggestions[:5]  # Limit to top 5 suggestions
    
    def get_nutrition_breakdown(self, nutrition_data: Dict[str, float]) -> Dict:
        """
        Create a detailed nutrition breakdown for visualization
        """
        if not nutrition_data:
            return {}
        
        breakdown = {
            'macronutrients': {},
            'other_nutrients': {}
        }
        
        # Macronutrients (calories from each) - USDA format
        calories = nutrition_data.get('Calories', 0)
        fat = nutrition_data.get('TotalFat', 0)
        protein = nutrition_data.get('Protein', 0)
        carbs = nutrition_data.get('Carbohydrate', 0)
        
        # Estimate carbs if not provided (rough estimation)
        if carbs == 0 and calories > 0:
            fat_calories = fat * 9
            protein_calories = protein * 4
            carb_calories = max(0, calories - fat_calories - protein_calories)
            carbs = carb_calories / 4
        
        breakdown['macronutrients'] = {
            'Calories': calories,
            'Fat': fat,
            'Protein': protein,
            'Carbohydrates': carbs
        }
        
        breakdown['other_nutrients'] = {
            'Sugar': nutrition_data.get('Sugar', 0),
            'Sodium': nutrition_data.get('Sodium', 0),
            'Saturated Fat': nutrition_data.get('SaturatedFat', 0),
            'Calcium': nutrition_data.get('Calcium', 0),
            'Iron': nutrition_data.get('Iron', 0),
            'Vitamin C': nutrition_data.get('VitaminC', 0)
        }
        
        return breakdown
    
    def compare_products(self, products: List[Dict]) -> Dict:
        """
        Compare multiple products and provide recommendations
        """
        if len(products) < 2:
            return {'error': 'Need at least 2 products to compare'}
        
        comparison = {
            'products': [],
            'winner': None,
            'comparison_metrics': {}
        }
        
        for product in products:
            analysis = self.analyze_product(**product)
            comparison['products'].append(analysis)
        
        # Determine winner based on health score
        valid_scores = [p['health_analysis']['score'] for p in comparison['products'] 
                       if p['health_analysis']['score'] is not None]
        
        if valid_scores:
            best_score = max(valid_scores)
            winner_idx = next(i for i, p in enumerate(comparison['products'])
                            if p['health_analysis']['score'] == best_score)
            comparison['winner'] = comparison['products'][winner_idx]
        
        return comparison

# Example usage
if __name__ == "__main__":
    analyzer = NutriAnalyzer()
    
    # Test analysis
    sample_nutrition = {
        'energy-kcal_100g': 350,
        'fat_100g': 12,
        'saturated-fat_100g': 4,
        'sugars_100g': 20,
        'fiber_100g': 6,
        'proteins_100g': 10,
        'sodium_100g': 0.8
    }
    
    result = analyzer.analyze_product(
        product_name="Sample Granola Bar",
        ingredients="oats, honey, almonds, dried fruit",
        nutrition_facts=sample_nutrition
    )
    
    print("Analysis Results:")
    print(f"Product: {result['product_name']}")
    print(f"Diet Type: {result['diet_classification']['diet_type']}")
    print(f"Health Score: {result['health_analysis']['score']:.1f}")
    print(f"Rating: {result['health_analysis']['rating']}")
    print("\nSuggestions:")
    for suggestion in result['suggestions']:
        print(f"  • {suggestion}")
