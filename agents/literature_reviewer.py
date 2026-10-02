from crewai import Agent
from tools.academic_search import academic_search_tool

def get_literature_reviewer(llm):
    return Agent(
        role='Academic Literature Reviewer',
        goal='Find and review academic papers and scholarly articles',
        backstory="A PhD-level researcher specializing in academic literature review.",
        verbose=True,
        allow_delegation=False,
        tools=[academic_search_tool],
        llm=llm
    )
