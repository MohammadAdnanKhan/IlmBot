import streamlit as st
import sys
from model.retriever import query_faiss
from model.generator import refine_with_gemini

# Windows compatibility for async
if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Page Config
st.set_page_config(
    page_title="IlmBot",
    page_icon="📖",
    layout="wide"
)

st.markdown("""
    <style>
        .main-container { background-color: #F8F9FA; padding: 10px; }
        .stChatMessage { border-radius: 12px; padding: 12px; margin: 8px 0; font-size: 16px; }
        .stChatMessage.user { background-color: #DCF8C6; text-align: right; border-radius: 15px; }
        .stChatMessage.assistant { background-color: #E6E6E6; text-align: left; border-radius: 15px; }
        .stChatContainer { max-height: 500px; overflow-y: auto; padding: 10px; }
        .stTitle { text-align: center; font-size: 28px; font-weight: bold; }
        .stInput { padding: 12px; border-radius: 10px; font-size: 16px; }
        .sidebar-title { text-align: center; font-size: 20px; font-weight: bold; }
        .sidebar-text { text-align: center; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

st.sidebar.image("logo.jpg")
st.sidebar.markdown("<h2 class='sidebar-title'>📖 IlmBot</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p class='sidebar-text'>Your Authentic Seerat Chatbot. Ask about the life of Prophet Muhammad (PBUH).</p>", unsafe_allow_html=True)

st.markdown("<h1 class='stTitle'>📖 IlmBot - Authentic Seerat Chatbot</h1>", unsafe_allow_html=True)
st.write("_Ask detailed questions for better responses._")

query = st.chat_input("Ask a question about the life of Prophet Muhammad (PBUH)...")

if query:
    with st.chat_message("user"):
        st.markdown(query)

    with st.spinner("Thinking..."):
        try:
            heading, retrieved_text = query_faiss(query)

            if retrieved_text and retrieved_text.lower() != "no relevant results found.":
                refined_answer = refine_with_gemini(query, retrieved_text)
            else:
                refined_answer = "⚠️ No relevant information found. Try rephrasing your question."

            response_text = f"""
            **📌 Retrieved Heading:** {heading}

            **🤖 IlmBot's Answer:**  
            {refined_answer}

            **📜 Source Text:**  
            {retrieved_text}
            """

        except Exception as e:
            response_text = f"⚠️ An error occurred: {str(e)}"

        with st.chat_message("assistant"):
            st.markdown(response_text)
