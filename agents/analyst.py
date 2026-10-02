from crewai import Agent

def get_analyst(llm):
    return Agent(
        role='Data Analyst',
        goal='Analyze the collected research and literature to extract key insights',
        backstory="An analytical mind that connects the dots between raw data and actionable intelligence.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
