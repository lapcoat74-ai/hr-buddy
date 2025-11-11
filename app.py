import streamlit as st
import pandas as pd
import time

# Simple page config
st.set_page_config(page_title="HR Buddy", layout="centered")

# Header
st.title("HR Buddy 🐶")
st.write("Your friendly HR assistant!")

# Simple dog
st.code("""
    / \\__
   (    @\\___
   /         O
  /   (_____/
 /_____/   U
""")

# Simple HR data
hr_data = {
    'annual leave': 'Full-time employees receive 14 paid annual leave days annually',
    'medical leave': 'Employees get 14 paid medical days annually', 
    'sick leave': 'Employees get 14 sick days annually',
    'probation': 'Probation is usually 6 months',
    'lunch break': 'We get a 1 hour break for lunch from 2pm to 3pm',
    'work from home': 'Remote work requires manager approval',
    'aws': 'The company does not apply AWS. Only performance based bonus'
}

# Simple chat function
def get_answer(question):
    question_lower = question.lower()
    
    if 'annual' in question_lower or 'vacation' in question_lower:
        return hr_data['annual leave']
    elif 'medical' in question_lower or 'sick' in question_lower:
        return hr_data['medical leave']
    elif 'probation' in question_lower:
        return hr_data['probation']
    elif 'lunch' in question_lower:
        return hr_data['lunch break']
    elif 'work from home' in question_lower or 'wfh' in question_lower:
        return hr_data['work from home']
    elif 'aws' in question_lower:
        return hr_data['aws']
    else:
        return "I'm not sure about that. Try asking about annual leave, medical leave, or probation!"

# Initialize chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm HR Buddy 🐶 How can I help you?"}
    ]

# Display chat
for message in st.session_state.messages:
    if message["role"] == "assistant":
        st.chat_message("assistant", avatar="🐶").write(message["content"])
    else:
        st.chat_message("user").write(message["content"])

# Chat input
if prompt := st.chat_input("Ask me about HR policies..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Get response
    response = get_answer(prompt)
    
    # Add assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant", avatar="🐶").write(response)
