from crewai import Agent
from tools.academic_search import academic_search_tool

def get_literature_reviewer(llm):
    return Agent(
        role='Academic Literature Reviewer',
        goal='Find and review academic papers and scholarly articles on the given topic',
        backstory="""A PhD-level researcher specializing in academic literature review.
        You use the academic search tool to find relevant papers, then summarize key findings concisely.""",
        verbose=True,
        allow_delegation=False,
        tools=[academic_search_tool],
        max_iter=3,
        llm=llm
    )
