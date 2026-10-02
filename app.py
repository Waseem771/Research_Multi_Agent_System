# --- STREAMLIT CLOUD SQLITE PATCH ---
# This fixes an issue where Streamlit Cloud's internal database version is too old for CrewAI
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import os
import re
from coordinator import run_research_system

# ==========================================
# 1. PAGE SETUP
# This sets up the browser tab name and icon
# ==========================================
st.set_page_config(
    page_title="Research Multi-Agent System",
    page_icon="🔬",
    layout="wide", # This makes the app take up the whole screen width
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. CUSTOM STYLING (CSS)
# This makes our buttons and boxes look pretty
# ==========================================
st.markdown("""
<style>
    .main {background-color: #f9f9fb;}
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #1e3a8a;
        color: white;
        font-weight: bold;
    }
    .agent-status {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e3a8a;
        padding: 10px;
        background: #e0e7ff;
        border-radius: 8px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. ADVANCED FEATURE: LIVE TERMINAL TRACKER
# (Beginners can ignore how this works, it just captures the AI's internal thoughts and prints them to the screen)
# ==========================================
class StreamToExpander:
    def __init__(self, status_container, log_container):
        self.status_container = status_container
        self.log_container = log_container
        self.logs = []
        
    def write(self, text):
        if text.strip():
            self.logs.append(text)
            self.log_container.code("".join(self.logs[-20:]), language='markdown') # Show last 20 lines
            
            # If the AI prints "Agent:", update the UI to show who is working!
            if "Agent:" in text:
                agent_name = text.split("Agent:")[-1].strip()
                self.status_container.markdown(f'<div class="agent-status">🤖 Currently Working: {agent_name}</div>', unsafe_allow_html=True)

    def flush(self):
        pass

# ==========================================
# 4. THE SIDEBAR (Left Menu)
# ==========================================
with st.sidebar:
    st.title("⚙️ Settings")
    st.write("Please enter your API Key. This acts as a password to use the AI brain.")
    
    # Create a text box for the password
    api_key = st.text_input("Groq API Key", type="password")
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key # Save it securely behind the scenes
    
    st.markdown("---")
    st.markdown("### 🧑‍🔬 Your AI Team:")
    st.markdown("- 🕵️ Lead Researcher\n- 📚 Lit Reviewer\n- 📊 Data Analyst\n- 🔍 Fact Checker\n- 👔 Orchestrator")

# ==========================================
# 5. THE MAIN SCREEN
# ==========================================
st.title("🔬 AI-Powered Research Team")
st.write("Type a topic below, and our 5 AI workers will write a detailed report for you.")

# Create the text box for the user's topic
topic = st.text_input("What do you want to learn about?", placeholder="Example: The future of artificial intelligence")

# Create a big button. When clicked, everything indented below it will run!
if st.button("🚀 Launch AI Team"):
    
    # Check if they forgot the API key
    if not os.environ.get("GROQ_API_KEY"):
        st.error("⚠️ Oops! You forgot to enter your Groq API Key in the left sidebar.")
        
    # Check if they forgot to type a topic
    elif not topic:
        st.warning("⚠️ Please type a topic first.")
        
    # If everything is good, start the AI!
    else:
        # Split the screen into two columns
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("📡 Live AI Brain Activity")
            status_container = st.empty() # Create an empty box to update later
            log_container = st.empty()    # Create an empty box for the logs
            
            status_container.markdown('<div class="agent-status">⏳ Waking up the AI...</div>', unsafe_allow_html=True)
            
            # Start tracking the AI's thoughts
            sys_stdout = sys.stdout
            sys.stdout = StreamToExpander(status_container, log_container)
            
            try:
                # 👉 THIS IS WHERE THE MAGIC HAPPENS! We call the manager from coordinator.py
                result = run_research_system(topic)
                
                status_container.success("✅ Finished!")
            except Exception as e:
                status_container.error(f"Something went wrong: {e}")
                result = None
            finally:
                sys.stdout = sys_stdout # Stop tracking thoughts

        with col2:
            st.subheader("📑 Final Report")
            if result:
                st.markdown(result) # Print the final text to the screen!
