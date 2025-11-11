# HR Chatbot - IMPROVED VERSION
import gspread
import pandas as pd
from google.colab import auth
from google.auth import default

print("🔐 Authenticating with Google...")
auth.authenticate_user()
creds, _ = default()

print("📊 Setting up Google Sheets connection...")
gc = gspread.authorize(creds)

# Your Google Sheet ID
SHEET_ID = "17kyGCoOQFUGyeAsdzxwUc51r5saoaQOSnl2Ugv4J5hI"

print("🔗 Opening your HR database...")
try:
    spreadsheet = gc.open_by_key(SHEET_ID)
    worksheet = spreadsheet.get_worksheet(0)
    all_data = worksheet.get_all_values()
    
    if len(all_data) > 1:
        df = pd.DataFrame(all_data[1:], columns=all_data[0])
        df = df.dropna(how='all')
        print(f"✅ Loaded {len(df)} HR policies")
        
    else:
        print("❌ No data found")
        df = None
        
except Exception as e:
    print(f"❌ Error: {e}")
    df = None

def understand_question_intent(question):
    """Improved intent detection with better priority"""
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
    """Improved search with better matching"""
    if df is None or len(df) == 0:
        return "Database not loaded"
    
    question_lower = question.lower().strip()
    
    # Find ALL possible matches
    possible_matches = []
    
    for index, row in df.iterrows():
        if pd.notna(row['Question']) and pd.notna(row['Answer']):
            sheet_question = str(row['Question']).lower().strip()
            sheet_answer = str(row['Answer'])
            score = 0
            
            # HIGHEST SCORE: Exact match with sheet question
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

def chat_with_hr_bot():
    print("\n" + "="*50)
    print("🤖 HR CHATBOT - IMPROVED VERSION")
    print("="*50)
    print("Now with better answer matching!")
    print("Type 'quit' to exit\n")
    
    while True:
        user_question = input("💬 You: ").strip()
        
        if user_question.lower() in ['quit', 'exit', 'bye']:
            print("👋 Goodbye!")
            break
            
        if user_question:
            answer = smart_search_hr_answer(user_question)
            print(f"✅ Bot: {answer}")
            print()

# Start the chatbot
if df is not None and len(df) > 0:
    chat_with_hr_bot()
else:
    print("🚫 Cannot start chatbot")
