import streamlit as st
import pandas as pd
import time
from difflib import SequenceMatcher
import requests
import io
import qrcode
from PIL import Image
import base64

# Page configuration
st.set_page_config(
    page_title="HR Buddy 🐶", 
    page_icon="🐕", 
    layout="centered"
)

# Custom CSS for cute styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #4ECDC4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .bubble {
        background: #E3F2FD;
        border-radius: 20px;
        padding: 15px;
        margin: 10px 0;
        border: 2px solid #BBDEFB;
        font-size: 16px;
    }
    .user-bubble {
        background: #FFEBEE;
        border: 2px solid #FFCDD2;
        margin-left: 20%;
    }
    .dog-bubble {
        background: #E8F5E8;
        border: 2px solid #C8E6C9;
        margin-right: 20%;
    }
    .dog-container {
        text-align: center;
        margin: 20px 0;
        font-family: monospace;
    }
    .qr-container {
        text-align: center;
        padding: 15px;
        background: #f8f9fa;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Header with cute dog
st.markdown('<h1 class="main-header">HR Buddy 🐶</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Your friendly HR assistant! Ask me about company policies!</p>', unsafe_allow_html=True)

# Cute dog ASCII art
dog_art = """
    / \\__
   (    @\\___
   /         O
  /   (_____/
 /_____/   U
"""

st.markdown(f'<div class="dog-container"><pre>{dog_art}</pre></div>', unsafe_allow_html=True)

# QR Code Generator
def generate_qr_code(url):
    """Generate QR code for the chatbot URL"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="#4ECDC4", back_color="white")
    return img

# Generate QR code for current app
chatbot_url = "https://d2nhanqr7atszvlsvzuvel.streamlit.app/"
qr_image = generate_qr_code(chatbot_url)

# Convert PIL Image to bytes for Streamlit
buf = io.BytesIO()
qr_image.save(buf, format="PNG")
qr_bytes = buf.getvalue()

# Load data from Public Google Sheet
@st.cache_data(ttl=300)
def load_google_sheet():
    try:
        SHEET_ID = "17kyGCoOQFUGyeAsdzxwUc51r5saoaQOSnl2Ugv4J5hI"
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
        response = requests.get(url)
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text))
        
        hr_data = {}
        for index, row in df.iterrows():
            if pd.notna(row.get('Question', '')) and pd.notna(row.get('Answer', '')):
                hr_data[str(row['Question']).lower().strip()] = row['Answer']
        
        st.sidebar.success(f"✅ Loaded {len(hr_data)} questions")
        return hr_data
        
    except Exception as e:
        st.sidebar.error(f"❌ Error: {e}")
        return {
            'annual leave': 'Full-time employees receive 14 paid annual leave days annually',
            'medical leave': 'Employees get 14 paid medical days annually',
            'sick leave': 'Employees get 14 sick days annually',
        }

hr_data = load_google_sheet()

# Your existing chatbot functions
def smart_similarity(user_question, stored_question):
    user_lower = user_question.lower()
    stored_lower = stored_question.lower()
    
    if user_lower == stored_lower:
        return 1.0
    if stored_lower in user_lower:
        return 0.9
    if user_lower in stored_lower:
        return 0.85
    
    user_words = set(user_lower.split())
    stored_words = set(stored_lower.split())
    common_words = user_words.intersection(stored_words)
    
    if common_words:
        word_score = len(common_words) / max(len(user_words), len(stored_words))
        important_words = ['leave', 'medical', 'sick', 'annual', 'probation', 'apply', 'how', 'many', 'days']
        bonus = sum(1 for word in important_words if word in user_lower and word in stored_lower) * 0.1
        return min(0.8, word_score + bonus)
    
    return SequenceMatcher(None, user_lower, stored_lower).ratio()

def find_best_answer(question):
    question_lower = question.lower().strip()
    best_match = None
    best_score = 0
    
    for stored_question, answer in hr_data.items():
        score = smart_similarity(question_lower, stored_question)
        
        if 'how' in question_lower and 'how' in stored_question:
            score += 0.15
        if 'apply' in question_lower and 'apply' in stored_question:
            score += 0.2
        if 'many' in question_lower and 'many' in stored_question:
            score += 0.15
        
        if score > best_score:
            best_score = score
            best_match = (stored_question, answer, score)
    
    return best_match

def smart_search_hr_answer(question):
    result = find_best_answer(question)
    if result and result[2] > 0.3:
        return result[1]
    else:
        return "I'm not sure about that. Try rephrasing your question!"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Woof woof! I'm HR Buddy! 🐶 I automatically read from your Google Sheet! What would you like to know?"}
    ]

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "assistant":
        with st.chat_message("assistant", avatar="🐶"):
            st.markdown(f'<div class="bubble dog-bubble">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        with st.chat_message("user", avatar="👤"):
            st.markdown(f'<div class="bubble user-bubble">{message["content"]}</div>', unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Ask HR Buddy about company policies..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(f'<div class="bubble user-bubble">{prompt}</div>', unsafe_allow_html=True)
    
    with st.chat_message("assistant", avatar="🐶"):
        with st.spinner("HR Buddy is thinking..."):
            time.sleep(1)
            response = smart_search_hr_answer(prompt)
            
            message_placeholder = st.empty()
            full_response = ""
            for chunk in response.split():
                full_response += chunk + " "
                time.sleep(0.05)
                message_placeholder.markdown(f'<div class="bubble dog-bubble">{full_response}▌</div>', unsafe_allow_html=True)
            message_placeholder.markdown(f'<div class="bubble dog-bubble">{response}</div>', unsafe_allow_html=True)
    
    st.session_state.messages.append({"role": "assistant", "content": response})

# Enhanced Sidebar with QR Code
with st.sidebar:
    st.header("📱 Share HR Buddy")
    
    # QR Code Section
    st.markdown('<div class="qr-container">', unsafe_allow_html=True)
    st.image(qr_bytes, caption="Scan to access HR Buddy", use_column_width=True)
    st.write("**Quick Link:**")
    st.code(chatbot_url, language="text")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.header("💡 Popular Questions")
    popular_questions = [
        "How much annual leave?",
        "Medical leave procedure?", 
        "Lunch break policy?",
        "Work from home?",
        "Probation period?"
    ]
    
    for q in popular_questions:
        if st.button(f"❓ {q}", key=q):
            st.session_state.messages.append({"role": "user", "content": q})
            st.rerun()
    
    st.header("📊 Stats")
    st.metric("Questions in Database", len(hr_data))
    
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.success("Data refreshed!")
        st.rerun()
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Chat cleared! How can I help you? 🐶"}
        ]
        st.rerun()

# Footer
st.markdown("---")
st.caption("HR Buddy 🐶 - Scan the QR code to share with colleagues!")
