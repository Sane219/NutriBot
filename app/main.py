import streamlit as st
from PIL import Image
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from ocr import OCRProcessor
from processor import NutriAnalyzer
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    # Page configuration
    st.set_page_config(
        page_title="NutriSnap: AI Food Health Analyzer",
        page_icon="🥗",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Header
    st.title("🥗 NutriSnap: AI Food Health Analyzer")
    st.markdown(
        "Upload an image of food packaging or enter product details to get comprehensive nutrition analysis, "
        "health scoring, and personalized dietary recommendations."
    )
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Analysis Options")
        analysis_mode = st.radio(
            "Choose analysis method:",
            ["📷 Image Upload", "✍️ Manual Entry"]
        )
        
        # Additional options
        st.subheader("⚙️ Settings")
        show_debug = st.checkbox("Show debug information", value=False)
        show_nutrition_breakdown = st.checkbox("Show detailed nutrition breakdown", value=True)
    
    # Initialize analyzer
    if 'analyzer' not in st.session_state:
        with st.spinner("Loading AI models..."):
            st.session_state.analyzer = NutriAnalyzer()
    
    analyzer = st.session_state.analyzer
    
    if analysis_mode == "📷 Image Upload":
        handle_image_upload(analyzer, show_debug, show_nutrition_breakdown)
    else:
        handle_manual_entry(analyzer, show_debug, show_nutrition_breakdown)

def handle_image_upload(analyzer, show_debug, show_nutrition_breakdown):
    """Handle image upload and OCR processing"""
    
    st.header("📷 Upload Food Package Image")
    
    uploaded_file = st.file_uploader(
        "Choose an image of food packaging...",
        type=["jpg", "jpeg", "png"],
        help="Upload a clear image of food packaging, ingredient list, or nutrition label"
    )
    
    # Validate file size (max 10MB)
    if uploaded_file is not None and uploaded_file.size > 10 * 1024 * 1024:
        st.error("File size too large. Please upload an image smaller than 10MB.")
        return
    
    if uploaded_file is not None:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            try:
                image = Image.open(uploaded_file)
                # Convert to RGB if necessary to ensure compatibility
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                st.image(image, caption='Uploaded Image', use_column_width=True)
            except Exception as e:
                st.error(f"Error loading image: {str(e)}")
                return
        
        with col2:
            with st.spinner("🔍 Extracting text from image..."):
                try:
                    ocr_processor = OCRProcessor()
                    ocr_result = ocr_processor.extract_text_from_image(image)
                except Exception as e:
                    st.error(f"Error processing image: {str(e)}")
                    return
            
            if show_debug and ocr_result:
                st.subheader("🔍 OCR Debug Information")
                st.write(f"**OCR Confidence**: {ocr_result.get('confidence', 0):.2%}")
                with st.expander("Raw extracted text"):
                    st.text(ocr_result.get('full_text', 'No text extracted'))
        
        # Extract nutrition values
        if ocr_result:
            nutrition_text = (ocr_result.get('nutrition_facts', '') + " " + 
                            ocr_result.get('full_text', ''))
            nutrition_values = ocr_processor.extract_nutrition_values(nutrition_text)
        else:
            nutrition_values = {}
        
        # Perform complete analysis
        if ocr_result:
            perform_analysis(
                analyzer,
                product_name=ocr_result.get('product_name', ''),
                ingredients=ocr_result.get('ingredients', ''),
                nutrition_facts=nutrition_values,
                show_debug=show_debug,
                show_nutrition_breakdown=show_nutrition_breakdown
            )
        else:
            st.error("Failed to extract information from the image. Please try with a clearer image or use manual entry.")

def handle_manual_entry(analyzer, show_debug, show_nutrition_breakdown):
    """Handle manual product entry"""
    
    st.header("✍️ Manual Product Entry")
    
    with st.form("product_form"):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            product_name = st.text_input("Product Name", placeholder="e.g., Organic Granola Bar")
            ingredients = st.text_area(
                "Ingredients List",
                placeholder="e.g., oats, honey, almonds, dried cranberries...",
                height=100
            )
        
        with col2:
            st.subheader("Nutrition Facts (per 100g)")
            
            col2a, col2b = st.columns([1, 1])
            with col2a:
                calories = st.number_input("Calories (kcal)", min_value=0.0, value=0.0, step=1.0)
                fat = st.number_input("Total Fat (g)", min_value=0.0, value=0.0, step=0.1)
                saturated_fat = st.number_input("Saturated Fat (g)", min_value=0.0, value=0.0, step=0.1)
                sugars = st.number_input("Sugars (g)", min_value=0.0, value=0.0, step=0.1)
            
            with col2b:
                fiber = st.number_input("Fiber (g)", min_value=0.0, value=0.0, step=0.1)
                protein = st.number_input("Protein (g)", min_value=0.0, value=0.0, step=0.1)
                sodium = st.number_input("Sodium (g)", min_value=0.0, value=0.0, step=0.001, format="%.3f")
        
        submitted = st.form_submit_button("🔍 Analyze Product", use_container_width=True)
        
        if submitted:
            # Create nutrition dictionary (USDA format)
            nutrition_facts = {}
            if calories > 0: nutrition_facts['Calories'] = calories
            if fat > 0: nutrition_facts['TotalFat'] = fat
            if saturated_fat > 0: nutrition_facts['SaturatedFat'] = saturated_fat
            if sugars > 0: nutrition_facts['Sugar'] = sugars
            if protein > 0: nutrition_facts['Protein'] = protein
            if sodium > 0: nutrition_facts['Sodium'] = sodium
            
            perform_analysis(
                analyzer,
                product_name=product_name,
                ingredients=ingredients,
                nutrition_facts=nutrition_facts,
                show_debug=show_debug,
                show_nutrition_breakdown=show_nutrition_breakdown
            )

def perform_analysis(analyzer, product_name, ingredients, nutrition_facts, show_debug, show_nutrition_breakdown):
    """Perform complete product analysis and display results"""
    
    if not any([product_name, ingredients, nutrition_facts]):
        st.warning("Please provide at least some product information to analyze.")
        return
    
    with st.spinner("🧠 Analyzing product with AI..."):
        results = analyzer.analyze_product(
            product_name=product_name,
            ingredients=ingredients,
            nutrition_facts=nutrition_facts
        )
    
    # Display results
    st.header("📊 Analysis Results")
    
    # Product info
    if product_name:
        st.subheader(f"📦 {product_name}")
    
    # Create three columns for main results
    col1, col2, col3 = st.columns([1, 1, 1])
    
    # Diet Classification
    with col1:
        diet_info = results['diet_classification']
        diet_type = diet_info['diet_type']
        confidence = diet_info['confidence']
        
        # Get emoji and color
        from models.diet_classifier import DietClassifier
        classifier = DietClassifier()
        emoji = classifier.get_diet_emoji(diet_type)
        color = classifier.get_diet_color(diet_type)
        
        st.markdown(f"### {emoji} Diet Classification")
        
        # Create a colored badge
        st.markdown(
            f'<div style="background-color: {color}; color: white; padding: 10px; '
            f'border-radius: 5px; text-align: center; font-weight: bold; margin: 10px 0;">{diet_type}</div>',
            unsafe_allow_html=True
        )
        
        st.write(f"**Confidence**: {confidence:.1%}")
        st.write(f"**Reason**: {diet_info['reason']}")
    
    # Health Score
    with col2:
        health_info = results['health_analysis']
        score = health_info.get('score')
        rating = health_info.get('rating', 'Unknown')
        
        st.markdown("### ❤️ Health Score")
        
        if score is not None:
            # Create a gauge chart
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Health Score"},
                delta = {'reference': 50},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 25], 'color': "lightgray"},
                        {'range': [25, 50], 'color': "yellow"},
                        {'range': [50, 75], 'color': "orange"},
                        {'range': [75, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig.update_layout(height=200)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown(f"**Rating**: {rating}")
        else:
            st.warning("Unable to calculate health score. Need nutrition data.")
    
    # Quick Stats
    with col3:
        st.markdown("### 📈 Quick Stats")
        
        if nutrition_facts:
            stats = [
                ("🔥 Calories", f"{nutrition_facts.get('Calories', 0):.0f} kcal"),
                ("🥜 Protein", f"{nutrition_facts.get('Protein', 0):.1f}g"),
                ("🍯 Sugar", f"{nutrition_facts.get('Sugar', 0):.1f}g"),
                ("🧂 Sodium", f"{nutrition_facts.get('Sodium', 0):.2f}mg")
            ]
            
            for icon_label, value in stats:
                st.write(f"**{icon_label}**: {value}")
        else:
            st.info("No nutrition data available")
    
    # Detailed nutrition breakdown
    if show_nutrition_breakdown and nutrition_facts:
        st.subheader("🍎 Detailed Nutrition Breakdown")
        
        breakdown = analyzer.get_nutrition_breakdown(nutrition_facts)
        
        if breakdown:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Macronutrients pie chart
                macros = breakdown['macronutrients']
                if any(macros.values()):
                    fig = px.pie(
                        values=[macros['Fat']*9, macros['Protein']*4, macros['Carbohydrates']*4],
                        names=['Fat', 'Protein', 'Carbohydrates'],
                        title="Macronutrient Calories Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Other nutrients bar chart
                others = breakdown['other_nutrients']
                if any(others.values()):
                    fig = px.bar(
                        x=list(others.keys()),
                        y=list(others.values()),
                        title="Other Nutrients (per 100g)",
                        labels={'x': 'Nutrient', 'y': 'Amount (g)'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    # Suggestions
    st.subheader("💡 Personalized Suggestions")
    suggestions = results['suggestions']
    
    if suggestions:
        for suggestion in suggestions:
            st.info(suggestion)
    else:
        st.info("No specific suggestions available for this product.")
    
    # Debug information
    if show_debug:
        st.subheader("🔧 Debug Information")
        with st.expander("Full analysis results"):
            st.json(results)
        
        with st.expander("Extracted ingredients"):
            st.write(ingredients)
        
        with st.expander("Nutrition data used"):
            st.write(nutrition_facts)

if __name__ == "__main__":
    main()

