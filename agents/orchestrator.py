from crewai import Agent

def get_orchestrator(llm):
    return Agent(
        role='Research Orchestrator',
        goal='Synthesize verified findings into a final polished Markdown report',
        backstory="""An expert project manager who oversees complex research operations.
        You synthesize all prior findings into one comprehensive, beautifully formatted Markdown report.
        You do NOT call any external tools.""",
        verbose=True,
        allow_delegation=False,
        tools=[],  # No tools — prevents Groq JSON parse failure on large inputs
        max_iter=3,
        llm=llm
    )
