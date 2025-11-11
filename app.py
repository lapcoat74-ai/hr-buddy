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

# Your HR data
sample_data = {
    'Question': [
        'annual leave', 'medical leave', 'sick leave', 'probation',
        'take medical leave during probation', 'apply medical leave', 
        'lunch break policy', 'work from home', 'aws', 'bonus'
    ],
    'Answer': [
        'Full-time employees receive 14 paid annual leave days annually',
        'Employees get 14 paid medical days annually',
        'Employees get 14 sick days annually, in Singapore we called it medical leave',
        'Probation is usually 6 months',
        'During the first 3 months of employment, you are not entitled to any paid leave including paid medical leave',
        'If you are sick, inform your direct supervisor and send MC to HP Partner',
        'We get a 1 hour break for lunch from 2pm to 3pm',
        'Remote work requires manager approval. Generally no WFH since COVID',
        'The company does not apply AWS. Only performance based bonus',
        'Performance bonus at management discretion at financial period end'
    ]
}

df = pd.DataFrame(sample_data)

# Chatbot logic
def understand_question_intent(question):
    question_lower = question.lower().strip()
    
    if any(word in question_lower for word in ['apply', 'how to', 'procedure']):
        if any(word in question_lower for word in ['mc', 'medical', 'sick']):
            return 'apply medical leave'
    
    if any(word in question_lower for word in ['how many', 'days']):
        if any(word in question_lower for word in ['medical', 'sick']):
            return 'sick leave'
    
    if any(word in question_lower for word in ['probation']):
        if any(word in question_lower for word in ['medical', 'sick']):
            return 'take medical leave during probation'
        return 'probation'
    
    if any(word in question_lower for word in ['work from home', 'wfh']):
        return 'work from home'
    
    if any(word in question_lower for word in ['aws']):
        return 'aws'
    
    if any(word in question_lower for word in ['lunch break', 'lunch']):
        return 'lunch break policy'
    
    if any(word in question_lower for word in ['bonus']):
        return 'bonus'
    
    if any(word in question_lower for word in ['medical leave', 'sick leave']):
        return 'medical leave'
    
    if any(word in question_lower for word in ['annual leave', 'vacation']):
        return 'annual leave'
    
    return None

def smart_search_hr_answer(question):
    topic_to_find = understand_question_intent(question)
    
    if topic_to_find:
        for index, row in df.iterrows():
            if str(row['Question']).lower().strip() == topic_to_find:
                return row['Answer']
    
    return "Woof! I'm not sure about that. Try asking about medical leave, annual leave, or probation! 🐶"

# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Woof woof! I'm HR Buddy! 🐶 Ask me about HR policies!"}
    ]

# Display chat history
for message in st.session_state.messages:
    if message["role"] == "assistant":
        with st.chat_message("assistant", avatar="🐶"):
            st.markdown(f'<div class="bubble dog-bubble">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        with st.chat_message("user", avatar="👤"):
            st.markdown(f'<div class="bubble user-bubble">{message["content"]}</div>', unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Ask HR Buddy..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(f'<div class="bubble user-bubble">{prompt}</div>', unsafe_allow_html=True)
    
    with st.chat_message("assistant", avatar="🐶"):
        with st.spinner("Thinking..."):
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

# Sidebar
with st.sidebar:
    st.header("💡 Try Asking:")
    st.write("- How much annual leave?")
    st.write("- Medical leave during probation?")
    st.write("- How to apply MC?")
    st.write("- Lunch break policy?")
    
    if st.button("Clear Chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Woof! Chat cleared! 🐶"}
        ]
        st.rerun()
