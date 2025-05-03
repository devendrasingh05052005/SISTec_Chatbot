import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import os

os.environ['GOOGLE_API_KEY'] =  'AIzaSyC3ngxiYZ67yopEwodhDAo37NICOP-yHZo'
# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="SISTec Assistant",
    page_icon="💬",
    layout="wide"
)

# Apply custom CSS for basic styling (simplified)
def apply_custom_css():
    st.markdown("""
    <style>
        /* Basic styling that works reliably in Streamlit */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        
        * {
            font-family: 'Inter', sans-serif;
        }
        
        .chat-message {
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            display: flex;
            flex-direction: column;
        }
        
        .chat-message.user {
            background-color: #2563eb;
            color: white;
            border-radius: 1rem 1rem 0 1rem;
            margin-left: 20%;
        }
        
        .chat-message.bot {
            background-color: #f3f4f6;
            color: #1f2937;
            border-radius: 1rem 1rem 1rem 0;
            margin-right: 20%;
        }
        
        .chat-header {
            background-color: #2563eb;
            color: white;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
        }
        
        .avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background-color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 1rem;
        }
        
        .avatar-text {
            color: #2563eb;
            font-weight: bold;
            font-size: 1.2rem;
        }
        
        .time-stamp {
            font-size: 0.8rem;
            opacity: 0.8;
            margin-top: 0.5rem;
            text-align: right;
        }
        
        .stButton button {
            background-color: #2563eb;
            color: white;
            border-radius: 2rem;
            padding: 0.5rem 1rem;
            border: none;
            font-weight: 500;
        }
        
        .quick-reply-container {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

# Cache the document loading
@st.cache_data
def load_docs():
    url = 'https://www.sistec.ac.in/'
    loader = WebBaseLoader(url)
    docs = loader.load()
    return docs[0].page_content

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "assistant", 
            "content": "Hi 👋 I'm the SISTec Chat Assistant. How can I help you today?", 
            "time": "Just now"
        }
    ]

# Quick reply options
QUICK_REPLIES = [
    "Admission Process",
    "Courses Offered",
    "Campus Facilities",
    "Faculty Information",
    "Placement Records"
]

def main():
    # Apply custom CSS
    apply_custom_css()
    
    # Load document content
    page_content = load_docs()
    
    # Setup LangChain components
    prompt = PromptTemplate(
        template='''Answer the following question about SISTec:
{question}

Base your response on this information:
{text}

Keep your response conversational, helpful, and concise. Include emojis where appropriate to make the conversation friendly.''',
        input_variables=['question', 'text']
    )
    model = ChatGoogleGenerativeAI(model='gemini-2.0-flash')
    parser = StrOutputParser()
    chain = prompt | model | parser
    
    # Create layout with columns
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        # Chat header
        st.markdown("""
        <div class="chat-header">
            <div class="avatar">
                <div class="avatar-text">🎓</div>
            </div>
            <div>
                <h3 style="margin:0">SISTec</h3>
                <p style="margin:0; font-size:0.9rem">We are online and ready to help!</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display chat messages
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user">
                    {message["content"]}
                    <div class="time-stamp">{message["time"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message bot">
                    {message["content"]}
                    <div class="time-stamp">{message["time"]}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Quick reply buttons - only show after the first bot message
        if len(st.session_state.chat_history) == 1:
            st.markdown('<div class="quick-reply-container">', unsafe_allow_html=True)
            cols = st.columns(len(QUICK_REPLIES))
            for i, (col, reply) in enumerate(zip(cols, QUICK_REPLIES)):
                with col:
                    if st.button(reply, key=f"quick_reply_{i}"):
                        # Add user message to chat history
                        st.session_state.chat_history.append({
                            "role": "user",
                            "content": reply,
                            "time": "Just now"
                        })
                        
                        # Generate response
                        response = chain.invoke({
                            'question': reply,
                            'text': page_content
                        })
                        
                        # Add assistant response to chat history
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": response,
                            "time": "Just now"
                        })
                        
                        # Rerun to update chat
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        # User input area
        user_input = st.text_input("Your message", placeholder="Type your message here...")
        
        # Send button
        if st.button("Send"):
            if user_input:
                # Add user message to chat history
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_input,
                    "time": "Just now"
                })
                
                # Generate response
                with st.spinner("Thinking..."):
                    response = chain.invoke({
                        'question': user_input,
                        'text': page_content
                    })
                
                # Add assistant response to chat history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response,
                    "time": "Just now"
                })
                
                # Clear the input
                st.rerun()

if __name__ == "__main__":
    main()