import streamlit as st
from main import create_or_load_vectorstore, get_answer
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="IRCTC Policy Chatbot",
    page_icon="🚂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for background and styling
st.markdown("""
<style>
    /* Main background with gradient */
    .stApp {
        background: linear-gradient(135deg, #023538 0%, #764ba2 100%);
        background-attachment: fixed;
    }

    /* Custom container for chat */
    .chat-container {
        background: rgba(0, 0, 0, 0.95);;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    /* Header styling */
    .main-header {
        text-align: center;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin-bottom: 30px;
    }

    /* Custom chat messages */
    .user-message {
        background: linear-gradient(135deg, #4CAF50, #45a049);
        color: white;
        padding: 15px;
        border-radius: 15px 15px 5px 15px;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    .assistant-message {
        background: linear-gradient(135deg, #023538, #45a049);
        color: white;
        padding: 15px;
        border-radius: 15px 15px 15px 5px;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    /* Sidebar styling */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }

    /* Input field styling */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.9);
        border: 2px solid #667eea;
        border-radius: 10px;
        padding: 10px;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }

    /* Statistics cards */
    .stat-card {
        background: rgba(255, 255, 255, 0.9);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin: 10px 0;
    }

    /* Loading animation */
    .loading-text {
        color: #667eea;
        font-weight: bold;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }

    /* Scroll to top button */
    .scroll-to-top {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #667eea;
        color: white;
        border: none;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        cursor: pointer;
        z-index: 1000;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.markdown("# 🚂 IRCTC Policy Chatbot")
st.markdown("### Your assistant for Indian Railways")
st.markdown('</div>', unsafe_allow_html=True)

with st.sidebar:
    # st.markdown("## 🎛️ Chat Controls")

    # Chat statistics
    # if "messages" in st.session_state:
    #     total_messages = len(st.session_state.messages)
    #     user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
    #     bot_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])

        # st.markdown(f"""
        # <div class="stat-card">
        #     <h4>📊 Chat Statistics</h4>
        #     <p><strong>Total Messages:</strong> {total_messages}</p>
        #     <p><strong>Your Questions:</strong> {user_messages}</p>
        #     <p><strong>Bot Responses:</strong> {bot_messages}</p>
        # </div>
        # """, unsafe_allow_html=True)

    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

    # Quick questions
    st.markdown("## 🔍 Quick Questions")
    quick_questions = [
        "What are the cancellation rules?",
        "How to book tickets online?",
        "What is the refund policy?",
        "Baggage allowance rules?",
        "Senior citizen concession?"
    ]

    for question in quick_questions:
        if st.button(question, key=f"quick_{question}"):
            st.session_state.pending_question = question
            st.rerun()

    # About section
    st.markdown("## ℹ️ About")
    st.markdown("""
    This chatbot helps you find information about:
    - 🎫 Ticket booking policies
    - 💰 Refund and cancellation rules
    - 🧳 Baggage guidelines
    - 👥 Passenger rights
    - 🚆 Train services
    """)


# Load FAISS index
@st.cache_resource
def get_db():
    return create_or_load_vectorstore()


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

# Load vector database
try:
    vec_db = get_db()
except Exception as e:
    st.error(f"❌ Error loading knowledge base: {str(e)}")
    st.stop()

# Main chat container
# st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display welcome message if no chat history
if not st.session_state.messages:
    st.markdown("""
    <div class="assistant-message">
        <h4>👋 Welcome to IRCTC Policy Chatbot!</h4>
        <p>I'm here to help you with all your IRCTC-related questions.</p>
        <p>How can I assist you today?</p>
    </div>
    """, unsafe_allow_html=True)

# Display chat history
for i, message in enumerate(st.session_state.messages):
    if message["role"] == "user":
        st.markdown(f"""
        <div class="user-message">
            <strong>You:</strong> {message["content"]}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="assistant-message">
            <strong>🤖 Assistant:</strong> {message["content"]}
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Handle pending question from quick buttons
if st.session_state.pending_question:
    query = st.session_state.pending_question
    st.session_state.pending_question = None

    # Add user message
    st.session_state.messages.append({"role": "user", "content": query})

    # Get and add bot response
    with st.spinner("Searching for an answer..."):
        answer = get_answer(query, vec_db)
        st.session_state.messages.append({"role": "assistant", "content": answer})

    st.rerun()

# Chat input
query = st.chat_input("💬 Ask me anything about IRCTC policies...")

if query:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": query})

    # Get bot response
    with st.spinner("Searching for an answer..."):
        start_time = time.time()
        answer = get_answer(query, vec_db)
        response_time = time.time() - start_time

        # Add response time to answer
        answer_with_time = f"{answer}\n\n*Response time: {response_time:.2f} seconds*"
        st.session_state.messages.append({"role": "assistant", "content": answer_with_time})

    st.rerun()

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: white; margin-top: 20px;">
    <p>🕐 Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>Made with ❤️ using Streamlit | Last updated: {datetime.now().strftime('%B %Y')}</p>
</div>
""", unsafe_allow_html=True)
