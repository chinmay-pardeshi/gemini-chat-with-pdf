from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load Gemini model
model = genai.GenerativeModel("models/gemma-3-27b-it")
chat = model.start_chat(history=[])

def get_gemini_response(question):
    return chat.send_message(question, stream=True)

# Streamlit app config
st.set_page_config(page_title="Q&A Demo")
st.title("💬 Gemini LLM Chatbot")

# Initialize chat history
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Display chat history first
st.subheader("Chat History")
for role, text in st.session_state['chat_history']:
    if role == "You":
        st.markdown(f"**🧑 You:** {text}")
    else:
        st.markdown(f"**🤖 Bot:** {text}")

# Spacer
st.markdown("---")

# Input at bottom
with st.form(key="user_input_form", clear_on_submit=True):
    input_text = st.text_input("Type your question:")
    submit = st.form_submit_button("Ask")

if submit and input_text:
    # Add user message
    st.session_state['chat_history'].append(("You", input_text))
    
    response_stream = get_gemini_response(input_text)
    full_response = ""

    for chunk in response_stream:
        try:
            if chunk.text:
                full_response += chunk.text
        except Exception as e:
            st.warning(f"Skipped a chunk: {e}")

    # Add bot message
    st.session_state['chat_history'].append(("Bot", full_response))
    st.rerun()  # Refresh to show updated chat history at the top
