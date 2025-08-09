import streamlit as st
import faiss 
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import time
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS


load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define a consistent path for the FAISS index
FAISS_INDEX_PATH = "faiss_index"

# Default models
EMBEDDING_MODEL = "models/embedding-001"  # Standard embedding model

# Available chat models - we'll let the user select one
AVAILABLE_CHAT_MODELS = [
    "models/gemini-1.0-pro",  # May have different quota
    "models/gemini-1.5-flash",  # Lower resource model with higher limits
    "models/gemini-1.5-pro",
    "models/gemini-1.5-flash-002",
    "models/gemini-1.5-pro-latest"
]

def get_pdf_text(pdf_docs):
    text = ""
    failed_files = []
    
    for pdf in pdf_docs:
        try:
            pdf_reader = PdfReader(pdf)
            for page in pdf_reader.pages:
                text += page.extract_text()
        except PdfReadError:
            failed_files.append(pdf.name)
        except Exception as e:
            failed_files.append(f"{pdf.name} (Error: {str(e)})")
    
    if failed_files:
        st.warning(f"Could not process the following files: {', '.join(failed_files)}")
        
    if not text:
        st.error("No valid PDF content could be extracted. Please upload valid PDF files.")
        return None
        
    return text


def get_text_chunks(text):
    if text is None:
        return []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks


def get_vector_store(text_chunks):
    if not text_chunks:
        return False
        
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
        
        # Create directory if it doesn't exist
        os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
        
        vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
        vector_store.save_local(FAISS_INDEX_PATH)
        return True
    except Exception as e:
        if "429" in str(e):
            st.error("Rate limit exceeded for embedding API. Please try again later or upgrade your Google API plan.")
        else:
            st.error(f"Error creating vector store: {str(e)}")
        return False


def get_conversational_chain(model_name):
    prompt_template = """
    Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is not in
    provided context just say, "answer is not available in the context", don't provide the wrong answer\n\n
    Context:\n {context}?\n
    Question: \n{question}\n

    Answer:
    """

    model = ChatGoogleGenerativeAI(model=model_name, temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    return chain


def handle_rate_limit_error(e):
    error_msg = str(e)
    if "429" in error_msg:
        # Try to parse the retry delay if available
        retry_seconds = 60  # Default retry time
        if "retry_delay" in error_msg and "seconds:" in error_msg:
            try:
                retry_part = error_msg.split("retry_delay")[1].split("seconds:")[1].split("}")[0].strip()
                retry_seconds = int(retry_part)
            except:
                pass
        
        st.error(f"Rate limit exceeded. API quota reached. Please try again after {retry_seconds} seconds or consider upgrading your Google API plan.")
        st.info("You can also try selecting a different model from the dropdown, as each model has separate quotas.")
    else:
        st.error(f"An error occurred: {error_msg}")


def get_response(user_question, selected_model):
    """Get response for a question and return it"""
    # Check if the index exists before trying to load it
    index_file = os.path.join(FAISS_INDEX_PATH, "index.faiss")
    if not os.path.exists(index_file):
        return "FAISS index not found. Please upload and process PDF files first."
    
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
        new_db = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
        docs = new_db.similarity_search(user_question)

        chain = get_conversational_chain(selected_model)
        
        response = chain(
            {"input_documents": docs, "question": user_question},
            return_only_outputs=True
        )

        return response["output_text"]
    except Exception as e:
        if "429" in str(e):
            return f"Rate limit exceeded. Please try again later or select a different model."
        else:
            return f"An error occurred: {str(e)}"


def display_chat_history():
    """Display the chat history"""
    if 'chat_history' in st.session_state and st.session_state.chat_history:
        st.subheader("💬 Chat History")
        
        for i, (question, answer) in enumerate(st.session_state.chat_history):
            # Question container
            with st.container():
                st.markdown(f"**🙋‍♂️ Question {i+1}:** {question}")
                
            # Answer container
            with st.container():
                st.markdown(f"**🤖 Answer:** {answer}")
                st.markdown("---")


def main():
    st.set_page_config(page_title="Chat PDF", layout="wide")
    st.header("Chat with PDF using Gemini💁")

    # Initialize session state
    if 'processed' not in st.session_state:
        st.session_state.processed = False
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'current_question' not in st.session_state:
        st.session_state.current_question = ""

    with st.sidebar:
        st.title("Menu:")
        
        # Model selection dropdown
        selected_model = st.selectbox(
            "Select Gemini Model", 
            options=AVAILABLE_CHAT_MODELS,
            index=1  # Default to gemini-1.5-flash which might have higher limits
        )
        
        pdf_docs = st.file_uploader("Upload your PDF Files and Click on the Submit & Process Button", accept_multiple_files=True)
        
        process_button = st.button("Submit & Process")
        
        if process_button:
            if not pdf_docs:
                st.error("Please upload at least one PDF file.")
            else:    
                with st.spinner("Processing..."):
                    raw_text = get_pdf_text(pdf_docs)
                    if raw_text:
                        text_chunks = get_text_chunks(raw_text)
                        if get_vector_store(text_chunks):
                            st.success("Done")
                            st.session_state.processed = True
                        else:
                            st.error("Failed to create vector store.")
        
        # Add clear chat history button
        if st.session_state.chat_history:
            st.markdown("---")
            if st.button("🗑️ Clear Chat History", type="secondary"):
                st.session_state.chat_history = []
                st.session_state.current_question = ""
                st.rerun()
        
        # Display quota and rate limit information
        st.markdown("---")
        st.subheader("About Rate Limits")
        st.info(
            "Google's free tier has strict rate limits that may cause '429 errors' when exceeded. "
            "Each model has separate quotas, so try different models if one hits limits. "
            "For production use, consider upgrading to a paid plan. "
            "[Learn more](https://ai.google.dev/gemini-api/docs/rate-limits)"
        )

    # Main chat area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Display chat history
        display_chat_history()
        
        # Question input at the bottom
        st.markdown("### Ask a New Question")
        
        # Create a form for the question input
        with st.form(key="question_form", clear_on_submit=True):
            user_question = st.text_input(
                "Type your question here:", 
                placeholder="Ask something about your PDF...",
                key="question_input"
            )
            submit_button = st.form_submit_button("Send", type="primary")
            
            if submit_button and user_question:
                if not st.session_state.processed:
                    st.warning("⚠️ Please upload and process PDF files first.")
                else:
                    # Show loading spinner
                    with st.spinner(f"🤔 Thinking... (using {selected_model})"):
                        # Get response
                        response = get_response(user_question, selected_model)
                        
                        # Add to chat history
                        st.session_state.chat_history.append((user_question, response))
                        
                        # Rerun to update the display
                        st.rerun()
    
    with col2:
        # Status panel
        st.markdown("### 📊 Status")
        
        if st.session_state.processed:
            st.success("✅ PDFs Processed")
        else:
            st.info("📤 Upload PDFs to start")
            
        st.markdown(f"**Current Model:** {selected_model}")
        st.markdown(f"**Total Questions:** {len(st.session_state.chat_history)}")
        
        if st.session_state.chat_history:
            st.markdown("**Recent Questions:**")
            # Show last 3 questions
            recent_questions = st.session_state.chat_history[-3:]
            for i, (q, _) in enumerate(reversed(recent_questions), 1):
                st.markdown(f"{i}. {q[:50]}{'...' if len(q) > 50 else ''}")


if __name__ == "__main__":
    main()
