# from dotenv import load_dotenv
# load_dotenv()   #loading all environment variables 

# import streamlit as st 
# import os 
# import google.generativeai as genai
# from PIL import Image

# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# # Function to load Gemini Pro model and get responses
# model =genai.GenerativeModel("models/learnlm-2.0-flash-experimental")
# # gemini-pro-vision

# def get_gemini_response(input,image):
#     if input!="":
#         response= model.generate_content([input,image])
#     else: 
#         response=model.generate_content(image)
#     return response.text

# st.set_page_config(page_title="Gemini Image Demo")
# st.header("Gemini Application")
# input=st.text_input("Inpt Prompt: ", key ="input")

# uploaded_file=st.file_uploader("Choose an Image...",type=["jpg","jpeg","png"])
# image=""
# if uploaded_file is not None:
#     image = Image.open(uploaded_file)
#     st.image(image,caption="Uploaded Image.",use_column_width=True)

# submit=st.button("Tell me about the image")


# # if submit is clicked
# if submit:
#     response = get_gemini_response(input,image)
#     st.subheader("The REsponse is ")
#     st.write(response)
#     # To install the PIL library (Pillow), you can use the following command:
#     # pip install pillow



from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image

# Load API key from .env
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize model
model = genai.GenerativeModel("models/learnlm-2.0-flash-experimental")

# Initialize session state for history
if "history" not in st.session_state:
    st.session_state.history = []  # stores list of (prompt, image, response)

# Function to get response from Gemini
def get_gemini_response(prompt, image):
    if prompt.strip() != "":
        response = model.generate_content([prompt, image])
    else:
        response = model.generate_content(image)
    return response.text

# Streamlit UI
st.set_page_config(page_title="🖼️ Gemini Image Demo")
st.header("📷 Gemini Vision Chat")

# Input prompt
prompt = st.text_input("Enter your prompt:", key="input")

# Image upload
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
image = None

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="🖼️ Uploaded Image", use_column_width=True)

# Submit button
submit = st.button("Tell me about the image")

# On click
if submit and image is not None:
    with st.spinner("Generating response..."):
        response = get_gemini_response(prompt, image)
    
    # Save to history
    st.session_state.history.append({
        "prompt": prompt,
        "image": image,
        "response": response
    })

# Display conversation history
if st.session_state.history:
    st.markdown("## 🕘 Conversation History")
    for i, item in enumerate(reversed(st.session_state.history), 1):
        st.markdown(f"### {len(st.session_state.history) - i + 1}. Prompt")
        st.markdown(f"**You:** {item['prompt'] or '*No prompt given*'}")
        st.image(item["image"], caption="Image used", use_column_width=True)
        st.markdown("**Gemini Response:**")
        st.markdown(item["response"])
        st.markdown("---")

