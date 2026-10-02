import os

def get_llm():
    # In recent versions of CrewAI, passing the litellm string format 
    # is the safest and most compatible way to configure the LLM.
    # CrewAI will automatically use the GROQ_API_KEY from os.environ
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables.")
    
    from crewai import LLM
    
    return LLM(
        model="groq/mixtral-8x7b-32768",
        api_key=groq_api_key,
        temperature=0.7
    )
