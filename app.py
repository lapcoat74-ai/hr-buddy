import streamlit as st
import pandas as pd
import time
from difflib import SequenceMatcher
import requests
import io

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

# Load data from Public Google Sheet
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_google_sheet():
    try:
        # Your Google Sheet ID (from the URL)
        SHEET_ID = "17kyGCoOQFUGyeAsdzxwUc51r5saoaQOSnl2Ugv4J5hI"
        
        # Export as CSV
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
        
        response = requests.get(url)
        response.raise_for_status()
        
        # Read CSV data
        df = pd.read_csv(io.StringIO(response.text))
        
        # Convert to dictionary
        hr_data = {}
        for index, row in df.iterrows():
            if pd.notna(row.get('Question', '')) and pd.notna(row.get('Answer', '')):
                hr_data[str(row['Question']).lower().strip()] = row['Answer']
        
        st.sidebar.success(f"✅ Loaded {len(hr_data)} questions from Google Sheets")
        return hr_data
        
    except Exception as e:
        st.sidebar.error(f"❌ Error loading Google Sheets: {e}")
        st.sidebar.info("Using fallback data...")
        # Fallback data
        return {
            'annual leave': 'Full-time employees receive 14 paid annual leave days annually',
            'medical leave': 'Employees get 14 paid medical days annually',
            'sick leave': 'Employees get 14 sick days annually',
            'probation': 'Probation is usually 6 months',
            'lunch break policy': 'We get a 1 hour break for lunch from 2pm to 3pm'
        }

# Load data from Google Sheets
hr_data = load_google_sheet()

# Display current questions in sidebar
with st.sidebar:
    st.header("📋 Available Questions")
    if hr_data:
        question_list = list(hr_data.keys())[:10]
        for q in question_list:
            st.write(f"• {q}")
        if len(hr_data) > 10:
            st.write(f"... and {len(hr_data) - 10} more")

def smart_similarity(user_question, stored_question):
    """Advanced similarity matching"""
    user_lower = user_question.lower()
    stored_lower = stored_question.lower()
    
    # Exact match
    if user_lower == stored_lower:
        return 1.0
    
    # One contains the other
    if stored_lower in user_lower:
        return 0.9
    if user_lower in stored_lower:
        return 0.85
    
    # Word overlap scoring
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
    """Finds the best matching answer"""
    question_lower = question.lower().strip()
    
    best_match = None
    best_score = 0
    
    for stored_question, answer in hr_data.items():
        score = smart_similarity(question_lower, stored_question)
        
        # Special boosts
        if 'how' in question_lower and 'how' in stored_question:
            score += 0.15
        if 'apply' in question_lower and 'apply' in stored_question:
            score += 0.2
        if 'many' in question_lower and 'many' in stored_question:
            score += 0.15
        
        if score > best_score:
            best_score = score
            best_match = (stored_question, answer, score)
    
    # Show matching info
    with st.sidebar:
        if best_match:
            st.write(f"**Best Match:** '{best_match[0]}'")
            st.write(f"**Confidence:** {best_match[2]:.1%}")
    
    return best_match

def smart_search_hr_answer(question):
    """Main function to find answers"""
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

# Sidebar with help
with st.sidebar:
    st.header("💡 How to Use")
    st.info("""
    **Just update your Google Sheet:**
    - Add new questions & answers
    - I'll auto-learn in 5 minutes!
    - No code changes needed!
    """)
    
    if st.button("🔄 Refresh from Google Sheets"):
        st.cache_data.clear()
        st.rerun()

# Footer
st.markdown("---")
st.caption("HR Buddy 🐶 - Connected to Google Sheets | Updates automatically!")
