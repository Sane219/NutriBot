import re
from typing import List, Union

class DietClassifier:
    """
    Classifies food products as Vegan, Vegetarian, or Non-Vegetarian
    based on ingredient lists or product information.
    """
    
    def __init__(self):
        # Non-vegetarian ingredients (meat, fish, etc.)
        self.non_veg_keywords = {
            # Meat products
            'beef', 'pork', 'chicken', 'turkey', 'duck', 'lamb', 'mutton', 'veal',
            'ham', 'bacon', 'sausage', 'pepperoni', 'salami', 'prosciutto',
            'meat', 'poultry', 'game', 'venison',
            
            # Fish and seafood
            'fish', 'salmon', 'tuna', 'cod', 'mackerel', 'sardine', 'anchovy',
            'shrimp', 'prawn', 'lobster', 'crab', 'oyster', 'mussel', 'clam',
            'scallop', 'squid', 'octopus', 'seafood', 'caviar',
            
            # Other animal products
            'gelatin', 'gelatine', 'carmine', 'cochineal', 'isinglass',
            'lard', 'tallow', 'suet', 'rennet', 'pepsin',
            
            # Animal fats
            'animal fat', 'beef fat', 'pork fat', 'chicken fat',
        }
        
        # Vegetarian but not vegan ingredients (dairy, eggs)
        self.vegetarian_keywords = {
            # Dairy products
            'milk', 'cream', 'butter', 'cheese', 'yogurt', 'yoghurt',
            'whey', 'casein', 'lactose', 'dairy', 'ghee',
            'mozzarella', 'cheddar', 'parmesan', 'feta', 'ricotta',
            
            # Eggs
            'egg', 'eggs', 'albumin', 'egg white', 'egg yolk',
            'mayonnaise', 'mayo',
            
            # Honey
            'honey', 'beeswax', 'propolis', 'royal jelly',
        }
        
        # Common vegan ingredients (for confidence boosting)
        self.vegan_keywords = {
            'vegetable', 'fruit', 'grain', 'legume', 'bean', 'lentil',
            'quinoa', 'rice', 'wheat', 'oat', 'barley', 'corn',
            'soy', 'tofu', 'tempeh', 'seitan', 'nuts', 'seeds',
            'coconut', 'almond', 'cashew', 'walnut', 'peanut',
            'olive oil', 'sunflower oil', 'canola oil', 'vegetable oil',
            'plant-based', 'vegan', 'plant protein',
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for analysis"""
        if not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace and punctuation
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _contains_keywords(self, text: str, keywords: set) -> bool:
        """Check if text contains any of the specified keywords"""
        cleaned_text = self._clean_text(text)
        
        for keyword in keywords:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, cleaned_text):
                return True
        
        return False
    
    def classify_by_ingredients(self, ingredients: Union[str, List[str]]) -> dict:
        """
        Classify diet type based on ingredients list
        
        Args:
            ingredients: String of ingredients or list of ingredient strings
            
        Returns:
            dict with classification result and confidence
        """
        # Handle different input types
        if isinstance(ingredients, list):
            ingredient_text = ' '.join(str(ing) for ing in ingredients)
        else:
            ingredient_text = str(ingredients) if ingredients else ""
        
        if not ingredient_text.strip():
            return {
                'diet_type': 'Unknown',
                'confidence': 0.0,
                'reason': 'No ingredient information provided'
            }
        
        # Check for non-vegetarian ingredients
        if self._contains_keywords(ingredient_text, self.non_veg_keywords):
            return {
                'diet_type': 'Non-Vegetarian',
                'confidence': 0.9,
                'reason': 'Contains meat, fish, or other animal-derived ingredients'
            }
        
        # Check for vegetarian (but not vegan) ingredients
        if self._contains_keywords(ingredient_text, self.vegetarian_keywords):
            return {
                'diet_type': 'Vegetarian',
                'confidence': 0.8,
                'reason': 'Contains dairy, eggs, or honey but no meat/fish'
            }
        
        # Check for explicit vegan indicators
        if self._contains_keywords(ingredient_text, self.vegan_keywords):
            return {
                'diet_type': 'Vegan',
                'confidence': 0.7,
                'reason': 'Contains only plant-based ingredients'
            }
        
        # Default to vegan if no animal products detected
        return {
            'diet_type': 'Vegan',
            'confidence': 0.6,
            'reason': 'No animal-derived ingredients detected'
        }
    
    def classify_by_product_info(self, product_name: str = "", 
                               categories: str = "", 
                               ingredients: str = "") -> dict:
        """
        Classify diet type using multiple product information sources
        
        Args:
            product_name: Name of the product
            categories: Product categories
            ingredients: Ingredients list
            
        Returns:
            dict with classification result and confidence
        """
        # Combine all available text
        combined_text = f"{product_name} {categories} {ingredients}"
        
        # Use ingredients-based classification
        result = self.classify_by_ingredients(combined_text)
        
        # Boost confidence if product name/categories also indicate diet type
        product_text = f"{product_name} {categories}".lower()
        
        if any(keyword in product_text for keyword in ['meat', 'chicken', 'beef', 'fish', 'salmon']):
            if result['diet_type'] == 'Non-Vegetarian':
                result['confidence'] = min(0.95, result['confidence'] + 0.1)
        
        elif any(keyword in product_text for keyword in ['cheese', 'milk', 'dairy', 'yogurt']):
            if result['diet_type'] == 'Vegetarian':
                result['confidence'] = min(0.9, result['confidence'] + 0.1)
        
        elif any(keyword in product_text for keyword in ['vegan', 'plant-based']):
            if result['diet_type'] == 'Vegan':
                result['confidence'] = min(0.95, result['confidence'] + 0.15)
        
        return result
    
    def get_diet_color(self, diet_type: str) -> str:
        """Get color code for diet type display"""
        color_map = {
            'Vegan': 'green',
            'Vegetarian': 'orange', 
            'Non-Vegetarian': 'red',
            'Unknown': 'gray'
        }
        return color_map.get(diet_type, 'gray')
    
    def get_diet_emoji(self, diet_type: str) -> str:
        """Get emoji for diet type"""
        emoji_map = {
            'Vegan': '🌱',
            'Vegetarian': '🥛',
            'Non-Vegetarian': '🥩',
            'Unknown': '❓'
        }
        return emoji_map.get(diet_type, '❓')

# Example usage and testing
if __name__ == "__main__":
    classifier = DietClassifier()
    
    # Test cases
    test_cases = [
        {
            'name': 'Chicken Sandwich',
            'ingredients': 'bread, chicken breast, lettuce, tomato, mayonnaise',
            'expected': 'Non-Vegetarian'
        },
        {
            'name': 'Cheese Pizza',
            'ingredients': 'wheat flour, tomato sauce, mozzarella cheese, olive oil',
            'expected': 'Vegetarian'
        },
        {
            'name': 'Vegetable Salad',
            'ingredients': 'lettuce, tomato, cucumber, olive oil, vinegar',
            'expected': 'Vegan'
        },
        {
            'name': 'Salmon Fillet',
            'ingredients': 'salmon, salt, pepper',
            'expected': 'Non-Vegetarian'
        }
    ]
    
    print("Diet Classification Test Results:")
    print("=" * 50)
    
    for test in test_cases:
        result = classifier.classify_by_ingredients(test['ingredients'])
        emoji = classifier.get_diet_emoji(result['diet_type'])
        
        print(f"\nProduct: {test['name']}")
        print(f"Ingredients: {test['ingredients']}")
        print(f"Classification: {emoji} {result['diet_type']}")
        print(f"Confidence: {result['confidence']:.1%}")
        print(f"Reason: {result['reason']}")
        print(f"Expected: {test['expected']} ✓" if result['diet_type'] == test['expected'] else f"Expected: {test['expected']} ✗")
