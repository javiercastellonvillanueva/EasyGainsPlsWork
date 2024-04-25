import streamlit as st
import base64
from PIL import Image
from io import BytesIO
import os

from anthropic import Anthropic

# Environment variable for API Key
api_key = "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"
client = Anthropic(api_key=api_key)

# Function to encode the image from an uploaded file or taken picture
def encode_image(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# Function to submit the image for analysis
def submit_image_prompt(base64_image, prompt):
    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "data": base64_image,
                                "media_type": "image/jpeg"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )
        return response
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Streamlit UI
st.title('EasyGains')
st.write('Upload an image of your meal for a full nutritional analysis')

if 'take_pic' not in st.session_state:
    st.session_state['take_pic'] = False

if st.button('Take A Picture With Your Device Camera'):
    st.session_state['take_pic'] = True

if st.session_state['take_pic']:
    takeapic = st.camera_input('Capture your meal')
    if takeapic is not None:
        st.session_state['captured_image'] = takeapic

uploaded_file = st.file_uploader('Upload from your device', type=['png', 'jpg', 'jpeg', 'heic', 'heif'], label_visibility='collapsed')

if st.button('Click Here to Analyze'):
    image = None
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
    elif 'captured_image' in st.session_state and st.session_state['captured_image'] is not None:
        image = Image.open(st.session_state['captured_image'])

    if image is None:
        st.error("Please upload a photo or take one to provide analysis.")
        st.stop()

    # Encode the uploaded or taken image
    base64_image = encode_image(image)

    prompt = "please estimate the total calories, grams of protein, grams of carbs, and grams of fats, the food in the image has. please say only that and nothing else. do not describe the food."
    response = submit_image_prompt(base64_image, prompt)
    
    if response:
        try:
            content = response.content
            st.success('Analysis complete!')
            for block in response.content:
                if block.type == "text":
                    st.write(block.text)
        except Exception as e:
            st.error(f"Failed to read the response: {e}")