from crewai import Agent

def get_analyst(llm):
    return Agent(
        role='Data Analyst',
        goal='Analyze the collected research and literature to extract key insights',
        backstory="""An analytical mind that connects the dots between raw data and actionable intelligence.
        You do NOT call any external tools. You reason over the data already provided to you.""",
        verbose=True,
        allow_delegation=False,
        tools=[],  # No tools — prevents Groq JSON parse failure on large inputs
        max_iter=3,
        llm=llm
    )
