import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

def get_llm():
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables.")
    
    return ChatGroq(
        api_key=groq_api_key,
        model="mixtral-8x7b-32768",
        temperature=0.7,
    )
