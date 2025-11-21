import streamlit as st
import pandas as pd
import time
from difflib import SequenceMatcher
import requests
import io
import re

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
            'probation': 'Probation is usually 6 months',
            'probation leave': 'During probation period, all leaves are considered no-pay leave',
        }

hr_data = load_google_sheet()

def is_nonsense_question(question):
    """Detect if the question is nonsense or gibberish"""
    question_lower = question.lower().strip()
    
    if len(question_lower) < 3:
        return True
    
    if re.match(r'^[^a-zA-Z]*$', question_lower):
        return True
    
    if re.match(r'^(.)\1+$', question_lower):
        return True
    
    if len(question_lower) > 10 and ' ' not in question_lower:
        random_char_ratio = len(re.findall(r'[aeiou]', question_lower)) / len(question_lower)
        if random_char_ratio < 0.1:
            return True
    
    nonsense_patterns = [
        'asdf', 'qwerty', 'zxcv', 'testing', 'test', 'hello', 'hi', 'hey',
        'abc', '123', 'lorem', 'ipsum'
    ]
    
    if any(pattern in question_lower for pattern in nonsense_patterns):
        return True
    
    return False

def smart_similarity(user_question, stored_question):
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
        important_words = ['leave', 'medical', 'sick', 'annual', 'probation', 'apply', 'how', 'many', 'days', 'policy', 'work', 'home', 'lunch', 'break', 'bonus', 'aws', 'compassionate', 'marriage']
        bonus = sum(1 for word in important_words if word in user_lower and word in stored_lower) * 0.1
        return min(0.8, word_score + bonus)
    
    return SequenceMatcher(None, user_lower, stored_lower).ratio()

def find_best_answer(question):
    question_lower = question.lower().strip()
    best_match = None
    best_score = 0
    
    # First check if it's nonsense
    if is_nonsense_question(question):
        return None, 0
    
    # Special handling for probation + leave combinations
    if any(word in question_lower for word in ['probation', 'probation period']):
        if any(word in question_lower for word in ['annual leave', 'medical leave', 'compassionate leave', 'marriage leave', 'leave']):
            # Boost scores for probation + leave questions
            for stored_question, answer in hr_data.items():
                if 'probation' in stored_question and any(leave in stored_question for leave in ['leave', 'annual', 'medical', 'compassionate', 'marriage']):
                    score = smart_similarity(question_lower, stored_question) + 0.3  # Big boost
                    if score > best_score:
                        best_score = score
                        best_match = (stored_question, answer, score)
            
            if best_match:  # If we found a probation+leave match, return it
                return best_match, best_score
    
    # Normal matching for other questions
    for stored_question, answer in hr_data.items():
        score = smart_similarity(question_lower, stored_question)
        
        # Special boosts for relevant patterns
        if 'how' in question_lower and 'how' in stored_question:
            score += 0.15
        if 'apply' in question_lower and 'apply' in stored_question:
            score += 0.2
        if 'many' in question_lower and 'many' in stored_question:
            score += 0.15
        if 'what' in question_lower and 'what' in stored_question:
            score += 0.1
        
        if score > best_score:
            best_score = score
            best_match = (stored_question, answer, score)
    
    return best_match, best_score

def smart_search_hr_answer(question):
    result, confidence = find_best_answer(question)
    
    # Debug info in sidebar
    with st.sidebar:
        if confidence > 0:
            st.write(f"**Confidence:** {confidence:.1%}")
            if result:
                st.write(f"**Matched:** '{result[0]}'")
    
    # High confidence: return the answer
    if result and confidence > 0.5:
        return result[1]
    
    # Low confidence or nonsense: ask for clarification
    else:
        return "I'm not sure I understand. Could you try rephrasing your question about HR policies? For example, you could ask about 'annual leave', 'medical leave during probation', or 'work from home' policies."

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
    st.header("💡 Tips")
    st.info("""
    **Try asking about:**
    - Annual leave during probation
    - Medical leave procedure  
    - Probation period leave
    - Work from home policy
    - Bonus and AWS
    """)
    
    st.header("🐕 About HR Buddy")
    st.write("""
    I'm your friendly HR assistant! 
    I'll try to understand your questions and give helpful answers about company policies.
    """)
    
    st.header("📊 Stats")
    st.metric("Questions in Database", len(hr_data))
    
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.success("Data refreshed!")
        st.rerun()
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Woof! Chat cleared! How can I help you? 🐶"}
        ]
        st.rerun()

# Footer
st.markdown("---")
st.caption("HR Buddy 🐶 - Your friendly HR assistant | Made with ❤️ for employees")
