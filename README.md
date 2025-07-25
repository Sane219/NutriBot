# NutriBot Project

## Overview
NutriBot is a web application that analyzes food packaging images to determine the healthiness of a product using AI and computer vision. It predicts a health score and classifies the diet type (vegan, vegetarian, or non-vegetarian) based on ingredients, while giving personalized dietary suggestions.

## Features
- **🤖 AI Health Scoring**: ML-powered health scoring (0-100) based on comprehensive nutrition analysis
- **🌱 Diet Classification**: Automatic classification as Vegan, Vegetarian, or Non-Vegetarian
- **📊 Nutrient Breakdown**: Interactive visualization of macronutrients, vitamins, and minerals
- **📷 OCR Analysis**: Extract nutrition facts from food packaging images
- **💡 Smart Suggestions**: Personalized dietary recommendations based on analysis
- **🎨 Modern UI**: Streamlit-powered responsive interface with interactive charts

## Technology Stack
- **Frontend**: Streamlit with Plotly visualizations
- **Image Processing**: EasyOCR for text extraction
- **Machine Learning**: Random Forest (Scikit-learn) trained on complete USDA dataset
- **Data Source**: USDA FoodData Central (7,058 foods with 16 nutritional attributes)
- **Backend**: Python with comprehensive nutrition analysis pipeline

## Getting Started

### Prerequisites
- [Python 3.7+](https://www.python.org/downloads/)

### Installation
1. **Clone the repository**
   ```bash
   git clone https://Sane219/NutriBot.git
   cd NutriBot
   ```
2. **Create a virtual environment**
   ```bash
   python -m venv nutribot_env
   source nutribot_env/bin/activate  # On Windows use: nutribot_env\Scripts\Activate
   ```
3. **Install dependencies**
   ```bash
   pip install --upgrade pip wheel
   pip install -r requirements.txt
   ```

### Running the App
Run the following command to start the Streamlit app.

```bash
python run_app.py
```

This will launch a Streamlit server. Access it by navigating to `http://localhost:8501` in your web browser.

## Usage
- **Image Upload:** Upload a clear photo of food packaging or an ingredient list to analyze.
- **Manual Entry:** Enter product details and nutrition facts manually if image upload isn't preferred.

## Development
The directory structure is divided into modules:
- **app/**: Core logic, OCR processing, and the Streamlit application.
- **models/**: Machine learning models for health scoring and diet classification.
- **data/**: Raw and processed dataset files.

Contributions are welcome! Feel free to submit issues or feature requests.

## License
This project is licensed under the MIT License. See `LICENSE` for more details.


