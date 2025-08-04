try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    print("Warning: EasyOCR not available. OCR functionality will be limited.")

import numpy as np
from PIL import Image
import re
from typing import List, Dict, Optional

class OCRProcessor:
    """
    Handles OCR extraction from food packaging images
    """
    
    def __init__(self):
        # Initialize EasyOCR reader for English if available
        if EASYOCR_AVAILABLE:
            try:
                self.reader = easyocr.Reader(['en'], gpu=False)
                self.ocr_available = True
            except Exception as e:
                print(f"Warning: Could not initialize EasyOCR: {e}")
                self.reader = None
                self.ocr_available = False
        else:
            self.reader = None
            self.ocr_available = False
    
    def extract_text_from_image(self, image) -> Dict[str, str]:
        """
        Extract text from uploaded image
        
        Args:
            image: PIL Image or numpy array
            
        Returns:
            Dict containing extracted text components
        """
        if not self.ocr_available:
            return {
                'full_text': 'OCR not available - EasyOCR not installed',
                'product_name': 'Unknown Product',
                'ingredients': 'Please install EasyOCR for text extraction',
                'nutrition_facts': '',
                'confidence': 0.0,
                'error': 'EasyOCR not available'
            }
        
        try:
            # Convert PIL Image to numpy array if needed
            if hasattr(image, 'convert'):
                image = np.array(image.convert('RGB'))
            
            # Use EasyOCR to extract text
            results = self.reader.readtext(image)
            
            # Combine all detected text
            full_text = ' '.join([result[1] for result in results])
            
            # Parse different components
            parsed_data = self._parse_extracted_text(full_text)
            
            # If we have text but no parsed components, try to extract at least something useful
            if full_text.strip() and not any(parsed_data.values()):
                # Look for any food-related words to use as product name
                food_words = ['bar', 'snack', 'cookie', 'chip', 'drink', 'juice', 'milk', 'bread', 'cereal']
                words = full_text.lower().split()
                
                for word in words:
                    if any(food_word in word for food_word in food_words):
                        parsed_data['product_name'] = word.title()
                        break
                
                # If still no product name, use first meaningful word
                if not parsed_data.get('product_name'):
                    meaningful_words = [w for w in words if len(w) > 3 and w.isalpha()]
                    if meaningful_words:
                        parsed_data['product_name'] = meaningful_words[0].title()
            
            return {
                'full_text': full_text,
                'product_name': parsed_data.get('product_name', ''),
                'ingredients': parsed_data.get('ingredients', ''),
                'nutrition_facts': parsed_data.get('nutrition_facts', ''),
                'confidence': self._calculate_confidence(results)
            }
            
        except Exception as e:
            return {
                'full_text': '',
                'product_name': '',
                'ingredients': '',
                'nutrition_facts': '',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _parse_extracted_text(self, text: str) -> Dict[str, str]:
        """
        Parse extracted text to identify different components
        """
        if not text or not text.strip():
            return {}
            
        text_lower = text.lower()
        result = {}
        
        # Try to extract product name (usually at the top, in larger text)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            # First non-empty line is likely the product name
            for line in lines:
                if len(line) > 3 and not any(keyword in line.lower() for keyword in ['ingredients', 'nutrition', 'calories', 'fat', 'protein']):
                    result['product_name'] = line
                    break
        
        # Try to extract ingredients with more flexible patterns
        ingredients_patterns = [
            r'ingredients?[:\s]+(.*?)(?=nutrition|allergen|contains|may contain|$)',
            r'contains?[:\s]+(.*?)(?=nutrition|allergen|$)',
            r'made with[:\s]+(.*?)(?=nutrition|allergen|$)'
        ]
        
        for pattern in ingredients_patterns:
            ingredients_match = re.search(pattern, text_lower, re.IGNORECASE | re.DOTALL)
            if ingredients_match:
                ingredients_text = ingredients_match.group(1).strip()
                if len(ingredients_text) > 5:  # Only if we got meaningful text
                    result['ingredients'] = ingredients_text
                    break
        
        # Try to extract nutrition information with more flexible patterns
        nutrition_patterns = [
            r'nutrition.*?facts?[:\s]+(.*?)(?=ingredients|allergen|$)',
            r'per\s+(?:100g?|serving)[:\s]+(.*?)(?=ingredients|allergen|$)',
            r'calories?[:\s]*\d+.*?(?=ingredients|allergen|$)',
            r'energy[:\s]*\d+.*?(?=ingredients|allergen|$)'
        ]
        
        for pattern in nutrition_patterns:
            nutrition_match = re.search(pattern, text_lower, re.IGNORECASE | re.DOTALL)
            if nutrition_match:
                nutrition_text = nutrition_match.group(0).strip()  # Get the full match
                if len(nutrition_text) > 5:  # Only if we got meaningful text
                    result['nutrition_facts'] = nutrition_text
                    break
        
        return result
    
    def _calculate_confidence(self, ocr_results: List) -> float:
        """
        Calculate overall confidence score from OCR results
        """
        if not ocr_results:
            return 0.0
        
        # Average confidence from all detected text
        confidences = [result[2] for result in ocr_results]
        return sum(confidences) / len(confidences)
    
    def extract_nutrition_values(self, text: str) -> Dict[str, float]:
        """
        Extract specific nutrition values from text
        
        Returns:
            Dict with nutrition values per 100g
        """
        nutrition_data = {}
        
        # Common patterns for nutrition values
        patterns = {
            'Calories': [
                r'calories?[:\s]*(\d+(?:\.\d+)?)',
                r'energy[:\s]*(\d+(?:\.\d+)?)\s*kcal',
                r'(\d+(?:\.\d+)?)\s*kcal'
            ],
            'TotalFat': [
                r'total\s+fat[:\s]*(\d+(?:\.\d+)?)',
                r'fat[:\s]*(\d+(?:\.\d+)?)\s*g'
            ],
            'SaturatedFat': [
                r'saturated\s+fat[:\s]*(\d+(?:\.\d+)?)',
                r'sat\.?\s+fat[:\s]*(\d+(?:\.\d+)?)'
            ],
            'Sugar': [
                r'sugars?[:\s]*(\d+(?:\.\d+)?)\s*g',
                r'total\s+sugars?[:\s]*(\d+(?:\.\d+)?)'
            ],
            'Protein': [
                r'protein[:\s]*(\d+(?:\.\d+)?)\s*g'
            ],
            'Sodium': [
                r'sodium[:\s]*(\d+(?:\.\d+)?)\s*(?:mg|g)',
                r'salt[:\s]*(\d+(?:\.\d+)?)\s*g'
            ],
            'Carbohydrate': [
                r'carbohydrates?[:\s]*(\d+(?:\.\d+)?)\s*g',
                r'total\s+carbs?[:\s]*(\d+(?:\.\d+)?)'
            ],
            'Calcium': [
                r'calcium[:\s]*(\d+(?:\.\d+)?)\s*(?:mg|g)'
            ],
            'Iron': [
                r'iron[:\s]*(\d+(?:\.\d+)?)\s*(?:mg|g)'
            ],
            'VitaminC': [
                r'vitamin\s+c[:\s]*(\d+(?:\.\d+)?)\s*(?:mg|g)',
                r'ascorbic\s+acid[:\s]*(\d+(?:\.\d+)?)'
            ]
        }
        
        text_lower = text.lower()
        
        for nutrient, regex_patterns in patterns.items():
            for pattern in regex_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    try:
                        value = float(match.group(1))
                        # Convert mg to g for sodium if needed
                        if nutrient == 'sodium_100g' and 'mg' in text_lower:
                            value = value / 1000
                        nutrition_data[nutrient] = value
                        break
                    except ValueError:
                        continue
        
        return nutrition_data

# Example usage and testing
if __name__ == "__main__":
    # Test with sample text
    ocr = OCRProcessor()
    
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
    
    # Test text parsing
    parsed = ocr._parse_extracted_text(sample_text)
    print("Parsed components:")
    for key, value in parsed.items():
        print(f"  {key}: {value}")
    
    # Test nutrition extraction
    nutrition = ocr.extract_nutrition_values(sample_text)
    print("\nExtracted nutrition values:")
    for key, value in nutrition.items():
        print(f"  {key}: {value}")
