from crewai import Agent

def get_orchestrator(llm):
    return Agent(
        role='Research Orchestrator',
        goal='Coordinate the research team and synthesize final findings',
        backstory="An expert project manager who oversees complex research operations.",
        verbose=True,
        allow_delegation=True,
        llm=llm
    )
