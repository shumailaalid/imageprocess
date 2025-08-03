import streamlit as st
import os
import subprocess
import sys
from PIL import Image
from io import BytesIO
import tempfile
import shutil
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Watercolor Step-by-Step Generator",
    page_icon="🎨",
    layout="wide"
)

# Initialize session state
if 'step_prompts' not in st.session_state:
    st.session_state.step_prompts = {
        "step1": "Generate ONLY a very light, minimal pencil sketch that captures the basic shapes and main contours from the original image. The lines should be extremely light and loose, just enough to guide the watercolor painting. This is typical watercolor preparation - barely visible guidelines on white watercolor paper.",
        
        "step2": "Create the first watercolor wash using very light, transparent colors. 1. Apply broad, light washes of the main color areas from the original image. 2. Use wet-on-wet technique - colors should blend and flow naturally. 3. Keep all colors very light and transparent - this is just the base layer. 4. Leave white paper areas for the lightest highlights completely untouched. 5. Use the light sketch as a guide but let the watercolor flow naturally beyond the lines. 6. Focus on establishing the basic color temperature and mood.",
        
        "step3": "Add a second layer of watercolor washes to build up color intensity. 1. Use the first wash as your foundation - work on DRY paper for more control. 2. Add slightly stronger, but still transparent colors in the medium-tone areas. 3. Begin to define shapes more clearly while maintaining watercolor's flowing quality. 4. Continue to preserve white paper highlights - once painted over, they cannot be recovered. 5. Use wet-on-dry technique for more defined edges where needed. 6. Layer transparent colors to create depth and richness.",
        
        "step4": "Build up medium tone values with careful watercolor layering. 1. Work from the previous wash layer, adding medium-strength transparent colors. 2. Begin to establish form and volume through careful value control. 3. Use a combination of wet-on-dry for controlled edges and wet-on-wet for soft transitions. 4. Maintain the luminosity characteristic of watercolor - avoid muddy colors. 5. Continue protecting white areas and light tones established in previous layers.",
        
        "step5": "Develop the shadow areas with stronger, but still transparent watercolor layers. 1. Build on the previous medium tone layer without losing its transparency. 2. Add deeper, richer colors in the shadow areas using multiple transparent glazes. 3. Maintain the wet, flowing quality of watercolor while gaining more control over shapes. 4. Use color temperature variations - warm and cool colors to create depth. 5. Allow some colors to blend naturally while controlling others with wet-on-dry technique.",
        
        "step6": "Add details and texture while maintaining watercolor's characteristic transparency. 1. Work from the shadow layer, adding carefully controlled details. 2. Use fine brushwork for details but keep the overall watercolor aesthetic. 3. Add texture through varied brushstrokes and controlled color bleeding. 4. Maintain the balance between detail and the loose, flowing quality of watercolor. 5. Use both wet-on-wet for soft details and wet-on-dry for crisp edges where appropriate.",
        
        "step7": "Add the deepest, darkest values to complete the tonal range of the watercolor painting. 1. Build from the detailed layer, adding only the very darkest shadow areas. 2. Use rich, concentrated watercolor pigments but maintain transparency. 3. These darks should be painted with confidence in single, decisive strokes. 4. Ensure the darkest values provide proper contrast with the preserved white highlights. 5. Maintain the luminous quality that makes watercolor distinctive.",
        
        "step8": "Complete the watercolor painting with final touches and refinements. 1. Build from the previous layer, making only subtle final adjustments. 2. Add any final small details or accents that enhance the overall composition. 3. Ensure the full range of values from pure white paper to deep darks is present. 4. Maintain the characteristic transparency, luminosity, and flowing quality of watercolor. 5. The finished painting should capture the spontaneous, fresh quality that makes watercolor unique. 6. Preserve the white of the paper for highlights - this is what gives watercolor its luminous quality."
    }

if 'system_prompt' not in st.session_state:
    st.session_state.system_prompt = """You are an expert watercolor painting generator that creates step-by-step paintings from photographs.
CRITICAL RULES YOU MUST ALWAYS FOLLOW:
1. NEVER add any objects, people, or elements that are not present in the original image
2. ALWAYS maintain the EXACT same composition as the reference images
3. ONLY add the specific elements requested in each step
4. Use transparent watercolor techniques - colors should be translucent and flow naturally
5. Preserve the original aspect ratio and resolution
6. Follow watercolor progression: light to dark, transparent layers, wet-on-wet and wet-on-dry techniques
7. Maintain white paper for highlights - watercolor cannot add white paint
8. Use proper watercolor color mixing and bleeding effects"""

def create_modified_script(api_key, image_path, system_prompt, step_prompts, output_dir):
    """Create a modified version of the watercolor script with custom prompts"""
    
    script_content = f'''import os
from PIL import Image
from io import BytesIO
from google import genai
from google.genai import types

# --- Configuration and Setup ---
client = genai.Client(api_key="{api_key}")

IMAGE_PATH = '{image_path}'
OUTPUT_DIR = '{output_dir}'

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    print(f"Created directory: {{OUTPUT_DIR}}")

try:
    original_image = Image.open(IMAGE_PATH)
    print(f"Loaded original image from {{IMAGE_PATH}}")
except FileNotFoundError:
    print(f"Error: The image file at '{{IMAGE_PATH}}' was not found.")
    exit()

SYSTEM_PROMPT = """{system_prompt}"""

def call_gemini_with_context(client, system_prompt, user_prompt, images, output_path, step_name):
    try:
        print(f"\\n--- Generating {{step_name}} ---")
        complete_prompt = f"{{system_prompt}}\\n\\n{{user_prompt}}"
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=[complete_prompt] + images,
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE']
            )
        )
        
        if response and response.candidates and response.candidates[0].content:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    generated_image = Image.open(BytesIO(part.inline_data.data))
                    generated_image.save(output_path)
                    print(f"{{step_name}} saved to: {{output_path}}")
                    return output_path, generated_image
        
        print(f"Could not find image data in the response for {{output_path}}.")
        return None, None
    except Exception as e:
        print(f"Error generating image for {{step_name}}: {{e}}")
        return None, None

if __name__ == "__main__":
    base_image = original_image
    
    # Step 1: Light Pencil Sketch
    step1_prompt = """{step_prompts['step1']}"""
    step1_path = os.path.join(OUTPUT_DIR, "step1_light_sketch.jpg")
    step1_path, light_sketch_image = call_gemini_with_context(
        client, SYSTEM_PROMPT, step1_prompt, [base_image], 
        step1_path, "Step 1: Light Pencil Sketch"
    )
    if not step1_path or not light_sketch_image:
        print("Could not generate light sketch. Exiting.")
        exit()
    
    # Step 2: First Light Wash
    step2_prompt = """{step_prompts['step2']}"""
    step2_path = os.path.join(OUTPUT_DIR, "step2_first_wash.jpg")
    step2_path, first_wash_image = call_gemini_with_context(
        client, SYSTEM_PROMPT, step2_prompt, [base_image, light_sketch_image], 
        step2_path, "Step 2: First Light Wash"
    )
    if not step2_path or not first_wash_image:
        print("Could not generate first wash. Exiting.")
        exit()
    
    # Step 3: Second Wash
    step3_prompt = """{step_prompts['step3']}"""
    step3_path = os.path.join(OUTPUT_DIR, "step3_second_wash.jpg")
    step3_path, second_wash_image = call_gemini_with_context(
        client, SYSTEM_PROMPT, step3_prompt, [base_image, first_wash_image], 
        step3_path, "Step 3: Second Wash - Building Color"
    )
    if not step3_path or not second_wash_image:
        print("Could not generate second wash. Exiting.")
        exit()
    
    # Step 4: Medium Tones
    step4_prompt = """{step_prompts['step4']}"""
    step4_path = os.path.join(OUTPUT_DIR, "step4_medium_tones.jpg")
    step4_path, medium_tones_image = call_gemini_with_context(
        client, SYSTEM_PROMPT, step4_prompt, [base_image, second_wash_image], 
        step4_path, "Step 4: Medium Tones"
    )
    if not step4_path or not medium_tones_image:
        print("Could not generate medium tones. Exiting.")
        exit()
    
    # Step 5: Shadows
    step5_prompt = """{step_prompts['step5']}"""
    step5_path = os.path.join(OUTPUT_DIR, "step5_shadows.jpg")
    step5_path, shadows_image = call_gemini_with_context(
        client, SYSTEM_PROMPT, step5_prompt, [base_image, medium_tones_image], 
        step5_path, "Step 5: Developing Shadows"
    )
    if not step5_path or not shadows_image:
        print("Could not generate shadows. Exiting.")
        exit()
    
    # Step 6: Details
    step6_prompt = """{step_prompts['step6']}"""
    step6_path = os.path.join(OUTPUT_DIR, "step6_details.jpg")
    step6_path, details_image = call_gemini_with_context(
        client, SYSTEM_PROMPT, step6_prompt, [base_image, shadows_image], 
        step6_path, "Step 6: Adding Details and Texture"
    )
    if not step6_path or not details_image:
        print("Could not generate details. Exiting.")
        exit()
    
    # Step 7: Darkest Values
    step7_prompt = """{step_prompts['step7']}"""
    step7_path = os.path.join(OUTPUT_DIR, "step7_darkest_values.jpg")
    step7_path, darkest_values_image = call_gemini_with_context(
        client, SYSTEM_PROMPT, step7_prompt, [base_image, details_image], 
        step7_path, "Step 7: Deepest Darks"
    )
    if not step7_path or not darkest_values_image:
        print("Could not generate darkest values. Exiting.")
        exit()
    
    # Step 8: Finished Painting
    step8_prompt = """{step_prompts['step8']}"""
    step8_path = os.path.join(OUTPUT_DIR, "step8_finished_watercolor.jpg")
    step8_path, finished_image = call_gemini_with_context(
        client, SYSTEM_PROMPT, step8_prompt, [base_image, darkest_values_image], 
        step8_path, "Step 8: Finished Watercolor Painting"
    )
    if not step8_path or not finished_image:
        print("Could not generate finished watercolor painting. Exiting.")
        exit()
    
    print(f"\\nWatercolor workflow completed. Check the '{{OUTPUT_DIR}}' folder for all generated watercolor painting steps.")
'''
    
    return script_content

def main():
    st.title("🎨 Watercolor Step-by-Step Generator")
    st.markdown("Generate beautiful watercolor paintings step-by-step using AI")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # API Key input
        api_key = st.text_input("Gemini API Key", type="password", help="Enter your Google Gemini API key")
        
        # Image upload
        uploaded_file = st.file_uploader("Upload Image", type=['jpg', 'jpeg', 'png'])
        
        if uploaded_file is not None:
            st.image(uploaded_file, caption="Input Image", width=200)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📝 System Prompt")
        st.session_state.system_prompt = st.text_area(
            "System Prompt", 
            value=st.session_state.system_prompt,
            height=200,
            help="This is the main instruction that guides the AI's behavior"
        )
        
        st.header("🎯 Step Prompts")
        
        step_names = [
            "Step 1: Light Pencil Sketch",
            "Step 2: First Light Wash", 
            "Step 3: Second Wash - Building Color",
            "Step 4: Medium Tones",
            "Step 5: Developing Shadows",
            "Step 6: Adding Details and Texture",
            "Step 7: Deepest Darks",
            "Step 8: Finished Watercolor Painting"
        ]
        
        for i, (step_key, step_name) in enumerate(zip(st.session_state.step_prompts.keys(), step_names)):
            with st.expander(step_name, expanded=False):
                st.session_state.step_prompts[step_key] = st.text_area(
                    f"Prompt for {step_name}",
                    value=st.session_state.step_prompts[step_key],
                    height=150,
                    key=f"prompt_{step_key}"
                )
    
    with col2:
        st.header("🚀 Generate Watercolor")
        
        if st.button("Generate Watercolor Steps", type="primary", disabled=not (api_key and uploaded_file)):
            if not api_key:
                st.error("Please enter your Gemini API key")
            elif not uploaded_file:
                st.error("Please upload an image")
            else:
                # Create temporary directories
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Save uploaded image
                    image_path = os.path.join(temp_dir, "input_image.jpg")
                    with open(image_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Create output directory
                    output_dir = os.path.join(temp_dir, "output")
                    
                    # Create modified script
                    script_content = create_modified_script(
                        api_key, image_path, st.session_state.system_prompt, 
                        st.session_state.step_prompts, output_dir
                    )
                    
                    # Save script
                    script_path = os.path.join(temp_dir, "watercolor_script.py")
                    with open(script_path, "w") as f:
                        f.write(script_content)
                    
                    # Run the script
                    with st.spinner("Generating watercolor steps... This may take several minutes."):
                        try:
                            result = subprocess.run(
                                [sys.executable, script_path],
                                capture_output=True,
                                text=True,
                                timeout=1800  # 30 minutes timeout
                            )
                            
                            if result.returncode == 0:
                                st.success("Watercolor generation completed!")
                                
                                # Display results
                                st.header("📸 Generated Watercolor Steps")
                                
                                step_files = [
                                    ("step1_light_sketch.jpg", "Step 1: Light Pencil Sketch"),
                                    ("step2_first_wash.jpg", "Step 2: First Light Wash"),
                                    ("step3_second_wash.jpg", "Step 3: Second Wash"),
                                    ("step4_medium_tones.jpg", "Step 4: Medium Tones"),
                                    ("step5_shadows.jpg", "Step 5: Developing Shadows"),
                                    ("step6_details.jpg", "Step 6: Adding Details"),
                                    ("step7_darkest_values.jpg", "Step 7: Deepest Darks"),
                                    ("step8_finished_watercolor.jpg", "Step 8: Finished Watercolor")
                                ]
                                
                                # Display images in a grid
                                for i in range(0, len(step_files), 2):
                                    cols = st.columns(2)
                                    for j, col in enumerate(cols):
                                        if i + j < len(step_files):
                                            filename, title = step_files[i + j]
                                            image_path = os.path.join(output_dir, filename)
                                            if os.path.exists(image_path):
                                                with col:
                                                    image = Image.open(image_path)
                                                    st.image(image, caption=title, use_column_width=True)
                                                    
                                                    # Add download button
                                                    with open(image_path, "rb") as file:
                                                        st.download_button(
                                                            label=f"Download {title}",
                                                            data=file.read(),
                                                            file_name=filename,
                                                            mime="image/jpeg"
                                                        )
                                
                                # Show console output
                                with st.expander("Console Output"):
                                    st.text(result.stdout)
                                    if result.stderr:
                                        st.text("Errors:")
                                        st.text(result.stderr)
                            
                            else:
                                st.error("Script execution failed!")
                                st.text("Error output:")
                                st.text(result.stderr)
                                st.text("Standard output:")
                                st.text(result.stdout)
                        
                        except subprocess.TimeoutExpired:
                            st.error("Script execution timed out after 30 minutes")
                        except Exception as e:
                            st.error(f"An error occurred: {str(e)}")
        
        # Instructions
        st.header("📋 Instructions")
        st.markdown("""
        1. **Enter your Gemini API Key** in the sidebar
        2. **Upload an image** that you want to convert to watercolor
        3. **Customize the system prompt** to change the overall AI behavior
        4. **Modify step prompts** to customize each watercolor stage
        5. **Click Generate** to create your step-by-step watercolor painting
        
        **Note:** The generation process may take several minutes as it creates 8 different watercolor steps.
        """)
        
        # Sample prompts section
        with st.expander("💡 Sample Prompt Ideas"):
            st.markdown("""
            **For portraits:**
            - Focus on skin tones and facial features
            - Emphasize soft, flowing hair textures
            - Preserve highlight areas on nose and cheeks
            
            **For landscapes:**
            - Start with sky washes and distant mountains
            - Build up foreground details gradually
            - Use wet-on-wet for atmospheric effects
            
            **For still life:**
            - Establish basic shapes first
            - Focus on light and shadow relationships
            - Add texture details in final steps
            """)

if __name__ == "__main__":
    main()