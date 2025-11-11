import streamlit as st
import pandas as pd
import time

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

# YOUR ACTUAL HR DATA - Copy from your Google Sheets
hr_data = {
    'annual leave': 'Full-time employees receive 14 paid annual leave days annually',
    'medical leave': 'Employees get 14 paid medical days annually',
    'maternity leave': 'Maternity leave policy provides 16 weeks of paid leave',
    'work from home': 'Remote work requires manager approval. In general, we do not practise work from home anymore since the end of COVID period',
    'health insurance': 'We do not have health insurance, we offer reimbursement of medical expenses of up to $200 instead.',
    'sick leave': 'Employees get 14 sick days annually, in Singapore we called it medical leave',
    'probation': 'Probation is usually 6 months',
    'take medical leave during probation': 'During the first 3 months of employment, you are not entitled to any paid leave including paid medical leave. Any medical leave taken during that period is considered unpaid leave',
    'aws': 'The company does not apply AWS for our employees. Only perfomance based bonus.',
    'bonus': 'The company applies performance bonus at the end of the financial period, at the managment\'s discretion',
    'apply annual leave': 'You need to seek permission from your direct supervisor, then apply it through the company\'s HRMS (Info-Tech). Once it is approved, you have to update your leave details on the company\'s google calender',
    'apply medical leave': 'If you are sick, you have to informed your direct supervisor at the ealiest time, and send a picture of your medical certification to the HP Partner',
    'what should i do if i am sick': 'If you are sick, you have to informed your direct supervisor at the ealiest time, and send a picture of your medical certification to the HP Partner',
    'company policy is unfair': 'Well too bad, you had signed the contract. Since you are onboard the pirate\'s ship there is NO WAY OUT!',
    'lunch break policy': 'We get a 1 hour break for lunch from 2pm to 3pm'
}

def understand_question_intent(question):
    """Improved intent detection"""
    question_lower = question.lower().strip()
    
    # HIGH PRIORITY: Application/process questions
    if any(word in question_lower for word in ['what if', 'what should', 'not feeling well', 'sick', 'unwell', 'dont feel well']):
        if any(word in question_lower for word in ['do', 'should', 'procedure', 'process']):
            return 'apply medical leave'
    
    if any(word in question_lower for word in ['apply', 'how to', 'procedure', 'process', 'steps']):
        if any(word in question_lower for word in ['mc', 'medical', 'sick']):
            return 'apply medical leave'
        elif any(word in question_lower for word in ['annual', 'vacation', 'leave']):
            return 'apply annual leave'
    
    # MEDIUM PRIORITY: Quantity questions
    if any(word in question_lower for word in ['how many', 'how much', 'days', 'entitled']):
        if any(word in question_lower for word in ['medical', 'sick', 'mc']):
            return 'sick leave'
        elif any(word in question_lower for word in ['annual', 'vacation']):
            return 'annual leave'
    
    # SPECIFIC COMBINATIONS
    if any(word in question_lower for word in ['probation', 'probation period']):
        if any(word in question_lower for word in ['medical leave', 'sick leave', 'mc', 'medical', 'take medical']):
            return 'take medical leave during probation'
        else:
            return 'probation'
    
    # GENERAL TOPICS
    if any(word in question_lower for word in ['work from home', 'remote work', 'wfh']):
        return 'work from home'
    
    if any(word in question_lower for word in ['aws', '13th month']):
        return 'aws'
    
    if any(word in question_lower for word in ['lunch break', 'lunch', 'break']):
        return 'lunch break policy'
    
    if any(word in question_lower for word in ['bonus', 'performance bonus']):
        return 'bonus'
    
    if any(word in question_lower for word in ['health insurance', 'medical insurance']):
        return 'health insurance'
    
    if any(word in question_lower for word in ['maternity', 'pregnancy']):
        return 'maternity leave'
    
    if any(word in question_lower for word in ['unfair', 'complain', 'pirate ship']):
        return 'company policy is unfair'
    
    # LOW PRIORITY: General terms
    if any(word in question_lower for word in ['medical leave', 'sick leave', 'mc']):
        return 'medical leave'
    
    if any(word in question_lower for word in ['annual leave', 'vacation', 'holiday']):
        return 'annual leave'
    
    return None

def search_hr_answer(question):
    """Search through the HR data"""
    question_lower = question.lower().strip()
    
    # Find ALL possible matches
    possible_matches = []
    
    for sheet_question, sheet_answer in hr_data.items():
        score = 0
        
        # HIGHEST SCORE: Exact match
        if question_lower == sheet_question:
            score += 100
        
        # HIGH SCORE: Intent-based matching
        intent = understand_question_intent(question)
        if intent and intent == sheet_question:
            score += 90
        
        # MEDIUM SCORE: Contains matching
        elif sheet_question in question_lower:
            score += 70
        elif question_lower in sheet_question:
            score += 60
        
        # LOW SCORE: Keyword matching
        else:
            sheet_words = set(sheet_question.split())
            user_words = set(question_lower.split())
            common_words = sheet_words.intersection(user_words)
            if common_words:
                score = len(common_words) * 10
        
        if score > 0:
            possible_matches.append({
                'score': score,
                'answer': sheet_answer,
                'question': sheet_question
            })
    
    # Select the best match
    if possible_matches:
        possible_matches.sort(key=lambda x: x['score'], reverse=True)
        return possible_matches[0]['answer']
    
    return None

def ask_deepseek(question):
    """AI fallback"""
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['apply', 'how to', 'procedure']):
        if any(word in question_lower for word in ['medical', 'sick', 'mc']):
            return "To apply for medical leave: Inform your supervisor and send MC to HP Partner."
    
    if any(word in question_lower for word in ['how many', 'days']):
        if any(word in question_lower for word in ['medical', 'sick']):
            return "Employees get 14 medical leave days annually."
    
    return "I'm not sure about that. Try asking about medical leave, annual leave, or other HR policies."

def smart_search_hr_answer(question):
    """HYBRID APPROACH"""
    database_answer = search_hr_answer(question)
    if database_answer:
        return database_answer
    
    return ask_deepseek(question)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Woof woof! I'm HR Buddy! 🐶 I can help you with questions about annual leave, medical leave, probation, and other HR policies! What would you like to know?"}
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
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message immediately
    with st.chat_message("user", avatar="👤"):
        st.markdown(f'<div class="bubble user-bubble">{prompt}</div>', unsafe_allow_html=True)
    
    # Get and display bot response
    with st.chat_message("assistant", avatar="🐶"):
        with st.spinner("HR Buddy is thinking..."):
            # Simulate thinking time
            time.sleep(1)
            response = smart_search_hr_answer(prompt)
            
            # Simulate typing animation
            message_placeholder = st.empty()
            full_response = ""
            for chunk in response.split():
                full_response += chunk + " "
                time.sleep(0.05)
                message_placeholder.markdown(f'<div class="bubble dog-bubble">{full_response}▌</div>', unsafe_allow_html=True)
            message_placeholder.markdown(f'<div class="bubble dog-bubble">{response}</div>', unsafe_allow_html=True)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar with help
with st.sidebar:
    st.header("💡 Tips")
    st.info("""
    **Try asking:**
    - How much annual leave?
    - Medical leave during probation?
    - How to apply MC?
    - Lunch break policy?
    - Do we have AWS?
    - Work from home policy?
    """)
    
    st.header("🐕 About HR Buddy")
    st.write("""
    I'm your friendly HR assistant! 
    I know all about company policies and I'm here to help you 24/7!
    
    **I can help with:**
    • Leave policies
    • Probation questions
    • Benefits information
    • Company procedures
    """)
    
    if st.button("Clear Chat History"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Woof! Chat cleared! How can I help you? 🐶"}
        ]
        st.rerun()

# Footer
st.markdown("---")
st.caption("HR Buddy 🐶 - Your friendly HR assistant | Made with ❤️ for employees")
