# from dotenv import load_dotenv
# load_dotenv()   #loading all environment variables from .env 

# import streamlit as st 
# import os 
# import google.generativeai as genai

# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# # Function to load Gemini Pro model and get responses
# model =genai.GenerativeModel("models/learnlm-2.0-flash-experimental")

# def get_gemini_response(question):
#     response= model.generate_content(question)
#     return response.text


# # Initialize our streamlit app
# st.set_page_config(page_title="Qestion and Answere Demo")

# st.header("Gemini LLM Application")

# input=st.text_input("Input:",key="input")
# submit=st.button("Ask the Question")

# # When submit is clicked 

# if submit:
#     response= get_gemini_response(input)
#     st.subheader("The Response is")
#     st.write(response)










from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize Gemini model
model = genai.GenerativeModel("models/learnlm-2.0-flash-experimental")

# Initialize Streamlit app
st.set_page_config(page_title="🖼️ Gemini Vision Chat", layout="centered")
st.title("📷 Gemini Vision Chat")
st.caption("Upload an image and ask questions — powered by Gemini + Streamlit")

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Function to get Gemini response
def get_gemini_response(prompt, image):
    if prompt.strip() != "":
        response = model.generate_content([prompt, image])
    else:
        response = model.generate_content(image)
    return response.text

# ---- Display Chat History at the Top ----
if st.session_state.chat_history:
    st.markdown("### 🕘 Conversation History")
    for idx, item in enumerate(reversed(st.session_state.chat_history), 1):
        st.markdown(f"**🗨️ You:** {item['prompt'] or '*No prompt given*'}")
        st.image(item["image"], caption="Image used", use_column_width=True)
        st.markdown(f"**🤖 Gemini:** {item['response']}")
        st.markdown("---")

# ---- Clear History Button ----
with st.sidebar:
    if st.button("🧹 Clear History"):
        st.session_state.chat_history = []
        st.rerun()


# ---- Input Section at Bottom ----
st.markdown("## 💬 Ask a Question")
prompt = st.text_input("Enter your prompt:", key="user_prompt")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
image = None

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="🖼️ Preview Image", use_column_width=True)

submit = st.button("🚀 Submit")

# Handle submission
if submit and image is not None:
    with st.spinner("Thinking..."):
        response = get_gemini_response(prompt, image)

    st.session_state.chat_history.append({
    "prompt": prompt,
    "image": image,
    "response": response
    })
    st.rerun()  # Reload to show updated history









