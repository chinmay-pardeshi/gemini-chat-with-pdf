# 📚 Gemini Chat with PDF
A powerful Streamlit-based application that allows users to upload PDF documents and interact with them using **Google's Gemini AI**. It extracts the text from the PDF and enables natural language Q&A based on the document content.

🌐 **[Live Demo on Streamlit Cloud](https://gemini-chat-with-pdf-version1.streamlit.app/)**  
---

## 🔍 Features
- 📄 Upload any **PDF document**
- 💬 Ask questions about the content
- 🤖 Get accurate, context-aware answers using **Gemini Pro**
- 🧠 Useful for research papers, eBooks, notes, reports, etc.

---

## 🎥 Demo GIF

![Demo](https://github.com/chinmay-pardeshi/gemini-chat-with-pdf/blob/main/demo/Chatwithpdf-gif.gif)

*Watch the full demo to see how easy it is to upload a PDF and start chatting with your documents!*




## 🧠 Powered By
- [Google Generative AI (Gemini)](https://ai.google.dev/)
- [Streamlit](https://streamlit.io/)
- [PyPDF2](https://pypi.org/project/PyPDF2/)
- [dotenv](https://pypi.org/project/python-dotenv/)

---

## 📁 Project Structure
```
gemini-chat-with-pdf/
│
├── app.py                # Main Streamlit application
├── .env                  # Environment variables (API key)
├── requirements.txt      # Python dependencies
└── README.md            # Project documentation
```

---

## 🛠️ Setup Instructions

#### 1. Clone the Repository
```bash
git clone https://github.com/your-username/gemini-chat-with-pdf.git
cd gemini-chat-with-pdf
```

#### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure Environment
Create a `.env` file with your API key:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

#### ▶️ Run the App
```bash
streamlit run app.py
```

