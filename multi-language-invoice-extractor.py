from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
from PIL import Image
import google.generativeai as genai

# Initialize Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("models/learnlm-2.0-flash-experimental")

# Setup session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "image_data" not in st.session_state:
    st.session_state.image_data = None

# Load and convert uploaded image
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Get Gemini response with chat context
def get_gemini_response(history, image):
    response = model.generate_content([*history, image[0]])
    return response.text

# UI setup
st.set_page_config(page_title="Multi-Language Invoice Extractor", layout="centered")
st.title("🧾 Multi-Language Invoice Extractor")

uploaded_file = st.file_uploader("Upload invoice image (jpg, png, jpeg)", type=["jpg", "jpeg", "png"])

# Load image once
if uploaded_file is not None and st.session_state.image_data is None:
    st.session_state.image_data = input_image_setup(uploaded_file)
    st.image(Image.open(uploaded_file), caption="Uploaded Invoice", use_column_width=True)

# Show message history
for i, msg in enumerate(st.session_state.messages):
    role = "user" if i % 2 == 0 else "assistant"
    with st.chat_message(role):
        st.markdown(msg)

# Input at bottom
if prompt := st.chat_input("Ask a question about the invoice"):
    # Show user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append(prompt)

    # Generate response
    response = get_gemini_response(st.session_state.messages, st.session_state.image_data)

    # Show assistant message
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append(response)
