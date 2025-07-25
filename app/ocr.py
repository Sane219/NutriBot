import easyocr
import numpy as np
from PIL import Image
import re
from typing import List, Dict, Optional

class OCRProcessor:
    """
    Handles OCR extraction from food packaging images
    """
    
    def __init__(self):
        # Initialize EasyOCR reader for English
        self.reader = easyocr.Reader(['en'], gpu=False)
    
    def extract_text_from_image(self, image) -> Dict[str, str]:
        """
        Extract text from uploaded image
        
        Args:
            image: PIL Image or numpy array
            
        Returns:
            Dict containing extracted text components
        """
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
        text_lower = text.lower()
        
        result = {}
        
        # Try to extract product name (usually at the top, in larger text)
        lines = text.split('\n')
        if lines:
            # First non-empty line is likely the product name
            for line in lines:
                if line.strip() and len(line.strip()) > 3:
                    result['product_name'] = line.strip()
                    break
        
        # Try to extract ingredients
        ingredients_match = re.search(r'ingredients?[:\s]+(.*?)(?=nutrition|allergen|$)', 
                                    text_lower, re.IGNORECASE | re.DOTALL)
        if ingredients_match:
            result['ingredients'] = ingredients_match.group(1).strip()
        
        # Try to extract nutrition information
        nutrition_patterns = [
            r'nutrition.*?facts?[:\s]+(.*?)(?=ingredients|allergen|$)',
            r'per\s+100g?[:\s]+(.*?)(?=ingredients|allergen|$)',
            r'calories?[:\s]+(.*?)(?=ingredients|allergen|$)'
        ]
        
        for pattern in nutrition_patterns:
            nutrition_match = re.search(pattern, text_lower, re.IGNORECASE | re.DOTALL)
            if nutrition_match:
                result['nutrition_facts'] = nutrition_match.group(1).strip()
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
