import re
from typing import List, Union

class DietClassifier:
    """
    Classifies food products as Pure Vegetarian, Vegetarian, or Non-Vegetarian
    based on Indian dietary standards and ingredient lists.
    
    Indian Classification:
    - Pure Vegetarian (Vegan): No animal products whatsoever
    - Vegetarian: Dairy products allowed, but no meat, fish, eggs, or onion/garlic
    - Non-Vegetarian: Contains meat, fish, eggs, or other animal flesh
    """
    
    def __init__(self):
        # Non-vegetarian ingredients (meat, fish, eggs - Indian standard)
        self.non_veg_keywords = {
            # Meat products
            'beef', 'pork', 'chicken', 'turkey', 'duck', 'lamb', 'mutton', 'veal',
            'ham', 'bacon', 'sausage', 'pepperoni', 'salami', 'prosciutto',
            'meat', 'poultry', 'game', 'venison', 'goat', 'buffalo',
            
            # Fish and seafood
            'fish', 'salmon', 'tuna', 'cod', 'mackerel', 'sardine', 'anchovy',
            'shrimp', 'prawn', 'lobster', 'crab', 'oyster', 'mussel', 'clam',
            'scallop', 'squid', 'octopus', 'seafood', 'caviar', 'hilsa', 'rohu',
            
            # Eggs (Non-veg in Indian standard)
            'egg', 'eggs', 'albumin', 'egg white', 'egg yolk', 'whole egg',
            'egg powder', 'dried egg', 'liquid egg', 'mayonnaise', 'mayo',
            
            # Other animal products
            'gelatin', 'gelatine', 'carmine', 'cochineal', 'isinglass',
            'lard', 'tallow', 'suet', 'rennet', 'pepsin', 'bone meal',
            
            # Animal fats
            'animal fat', 'beef fat', 'pork fat', 'chicken fat', 'fish oil',
            
            # Additives from animals
            'l-cysteine', 'shellac', 'lanolin', 'stearic acid', 'glycerin from animal',
        }
        
        # Vegetarian ingredients (dairy allowed, but not pure vegan)
        self.vegetarian_keywords = {
            # Dairy products
            'milk', 'cream', 'butter', 'cheese', 'yogurt', 'yoghurt',
            'whey', 'casein', 'lactose', 'dairy', 'ghee', 'paneer',
            'mozzarella', 'cheddar', 'parmesan', 'feta', 'ricotta',
            'condensed milk', 'evaporated milk', 'milk powder', 'buttermilk',
            'khoya', 'mawa', 'rabri', 'malai', 'dahi', 'lassi',
            
            # Honey and bee products
            'honey', 'beeswax', 'propolis', 'royal jelly',
        }
        
        # Pure vegetarian (vegan) ingredients
        self.pure_veg_keywords = {
            # Vegetables and fruits
            'vegetable', 'fruit', 'tomato', 'potato', 'carrot', 'spinach',
            'cauliflower', 'broccoli', 'cabbage', 'peas', 'beans',
            
            # Grains and cereals
            'rice', 'wheat', 'flour', 'oat', 'barley', 'corn', 'millet',
            'quinoa', 'buckwheat', 'ragi', 'bajra', 'jowar',
            
            # Legumes and pulses
            'dal', 'lentil', 'chickpea', 'kidney bean', 'black bean',
            'moong', 'masoor', 'chana', 'rajma', 'urad', 'toor',
            
            # Plant proteins
            'soy', 'tofu', 'tempeh', 'seitan', 'plant protein',
            
            # Nuts and seeds
            'almond', 'cashew', 'walnut', 'peanut', 'pistachio',
            'sesame', 'sunflower seed', 'pumpkin seed', 'chia seed',
            
            # Plant oils
            'coconut oil', 'olive oil', 'sunflower oil', 'mustard oil',
            'sesame oil', 'groundnut oil', 'vegetable oil',
            
            # Spices and herbs (excluding onion/garlic for Jain consideration)
            'turmeric', 'cumin', 'coriander', 'cardamom', 'cinnamon',
            'clove', 'black pepper', 'ginger', 'mint', 'basil',
            
            # Explicit markers
            'plant-based', 'vegan', 'pure vegetarian', 'no animal products',
        }
        
        # Ingredients that make food non-vegetarian for some communities
        self.jain_restricted = {
            'onion', 'garlic', 'potato', 'carrot', 'radish', 'beetroot',
            'ginger', 'turnip', 'leek', 'shallot', 'scallion'
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
    
    def classify_by_ingredients(self, ingredients: Union[str, List[str]], 
                              check_jain_restrictions: bool = False) -> dict:
        """
        Classify diet type based on ingredients list using Indian standards
        
        Args:
            ingredients: String of ingredients or list of ingredient strings
            check_jain_restrictions: Whether to check for Jain dietary restrictions
            
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
        
        # Check for non-vegetarian ingredients (includes eggs in Indian standard)
        if self._contains_keywords(ingredient_text, self.non_veg_keywords):
            return {
                'diet_type': 'Non-Vegetarian',
                'confidence': 0.95,
                'reason': 'Contains meat, fish, eggs, or other non-vegetarian ingredients'
            }
        
        # Check for vegetarian ingredients (dairy allowed)
        if self._contains_keywords(ingredient_text, self.vegetarian_keywords):
            return {
                'diet_type': 'Vegetarian',
                'confidence': 0.85,
                'reason': 'Contains dairy products but no non-vegetarian ingredients'
            }
        
        # Check for Jain restrictions if requested
        if check_jain_restrictions and self._contains_keywords(ingredient_text, self.jain_restricted):
            return {
                'diet_type': 'Vegetarian',
                'confidence': 0.75,
                'reason': 'Contains root vegetables (not suitable for Jain diet)'
            }
        
        # Check for explicit pure vegetarian indicators
        if self._contains_keywords(ingredient_text, self.pure_veg_keywords):
            return {
                'diet_type': 'Pure Vegetarian',
                'confidence': 0.8,
                'reason': 'Contains only plant-based ingredients'
            }
        
        # Default to pure vegetarian if no animal products detected
        return {
            'diet_type': 'Pure Vegetarian',
            'confidence': 0.65,
            'reason': 'No animal-derived ingredients detected'
        }
    
    def classify_by_product_info(self, product_name: str = "", 
                               categories: str = "", 
                               ingredients: str = "",
                               check_jain_restrictions: bool = False) -> dict:
        """
        Classify diet type using multiple product information sources
        
        Args:
            product_name: Name of the product
            categories: Product categories
            ingredients: Ingredients list
            check_jain_restrictions: Whether to check for Jain dietary restrictions
            
        Returns:
            dict with classification result and confidence
        """
        # Combine all available text
        combined_text = f"{product_name} {categories} {ingredients}"
        
        # Use ingredients-based classification
        result = self.classify_by_ingredients(combined_text, check_jain_restrictions)
        
        # Boost confidence if product name/categories also indicate diet type
        product_text = f"{product_name} {categories}".lower()
        
        # Non-vegetarian indicators
        non_veg_indicators = ['meat', 'chicken', 'mutton', 'fish', 'egg', 'prawn', 'crab']
        if any(keyword in product_text for keyword in non_veg_indicators):
            if result['diet_type'] == 'Non-Vegetarian':
                result['confidence'] = min(0.98, result['confidence'] + 0.1)
        
        # Vegetarian indicators
        veg_indicators = ['paneer', 'cheese', 'milk', 'dairy', 'ghee', 'butter']
        if any(keyword in product_text for keyword in veg_indicators):
            if result['diet_type'] == 'Vegetarian':
                result['confidence'] = min(0.92, result['confidence'] + 0.1)
        
        # Pure vegetarian indicators
        pure_veg_indicators = ['vegan', 'plant-based', 'pure veg', 'no dairy', 'dairy-free']
        if any(keyword in product_text for keyword in pure_veg_indicators):
            if result['diet_type'] == 'Pure Vegetarian':
                result['confidence'] = min(0.95, result['confidence'] + 0.15)
        
        return result
    
    def get_diet_color(self, diet_type: str) -> str:
        """Get color code for diet type display"""
        color_map = {
            'Pure Vegetarian': 'green',
            'Vegetarian': 'orange', 
            'Non-Vegetarian': 'red',
            'Unknown': 'gray'
        }
        return color_map.get(diet_type, 'gray')
    
    def get_diet_emoji(self, diet_type: str) -> str:
        """Get emoji for diet type"""
        emoji_map = {
            'Pure Vegetarian': '🌱',
            'Vegetarian': '🥛',
            'Non-Vegetarian': '🍖',
            'Unknown': '❓'
        }
        return emoji_map.get(diet_type, '❓')
    
    def get_diet_symbol(self, diet_type: str) -> str:
        """Get Indian dietary symbols"""
        symbol_map = {
            'Pure Vegetarian': '🟢',  # Green dot
            'Vegetarian': '🟢',       # Green dot  
            'Non-Vegetarian': '🔴',   # Red dot
            'Unknown': '⚪'           # White dot
        }
        return symbol_map.get(diet_type, '⚪')

# Example usage and testing
if __name__ == "__main__":
    classifier = DietClassifier()
    
    # Test cases for Indian dietary standards
    test_cases = [
        {
            'name': 'Chicken Biryani',
            'ingredients': 'basmati rice, chicken, onion, garlic, ghee, spices',
            'expected': 'Non-Vegetarian'
        },
        {
            'name': 'Paneer Butter Masala',
            'ingredients': 'paneer, tomato, cream, butter, onion, garlic, spices',
            'expected': 'Vegetarian'
        },
        {
            'name': 'Dal Tadka',
            'ingredients': 'toor dal, turmeric, cumin, mustard seeds, curry leaves, oil',
            'expected': 'Pure Vegetarian'
        },
        {
            'name': 'Egg Curry',
            'ingredients': 'eggs, onion, tomato, coconut milk, spices',
            'expected': 'Non-Vegetarian'
        },
        {
            'name': 'Chole Bhature',
            'ingredients': 'chickpeas, wheat flour, yogurt, oil, spices',
            'expected': 'Vegetarian'
        },
        {
            'name': 'Vegetable Pulao',
            'ingredients': 'basmati rice, mixed vegetables, cumin, bay leaves, oil',
            'expected': 'Pure Vegetarian'
        },
        {
            'name': 'Fish Curry',
            'ingredients': 'fish, coconut, curry leaves, tamarind, spices',
            'expected': 'Non-Vegetarian'
        }
    ]
    
    print("Indian Diet Classification Test Results:")
    print("=" * 60)
    
    for test in test_cases:
        result = classifier.classify_by_ingredients(test['ingredients'])
        emoji = classifier.get_diet_emoji(result['diet_type'])
        symbol = classifier.get_diet_symbol(result['diet_type'])
        
        print(f"\nDish: {test['name']}")
        print(f"Ingredients: {test['ingredients']}")
        print(f"Classification: {symbol} {emoji} {result['diet_type']}")
        print(f"Confidence: {result['confidence']:.1%}")
        print(f"Reason: {result['reason']}")
        status = "✓" if result['diet_type'] == test['expected'] else "✗"
        print(f"Expected: {test['expected']} {status}")
    
    # Test Jain restrictions
    print(f"\n{'='*60}")
    print("Testing Jain Dietary Restrictions:")
    jain_test = {
        'name': 'Aloo Gobi',
        'ingredients': 'potato, cauliflower, onion, turmeric, oil'
    }
    
    normal_result = classifier.classify_by_ingredients(jain_test['ingredients'])
    jain_result = classifier.classify_by_ingredients(jain_test['ingredients'], check_jain_restrictions=True)
    
    print(f"\nDish: {jain_test['name']}")
    print(f"Ingredients: {jain_test['ingredients']}")
    print(f"Normal Classification: {classifier.get_diet_symbol(normal_result['diet_type'])} {normal_result['diet_type']}")
    print(f"Jain Classification: {classifier.get_diet_symbol(jain_result['diet_type'])} {jain_result['diet_type']}")
    print(f"Jain Reason: {jain_result['reason']}")
