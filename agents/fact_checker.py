from crewai import Agent
from tools.citation_checker import citation_checker_tool

def get_fact_checker(llm):
    return Agent(
        role='Rigorous Fact Checker',
        goal='Verify all claims, data points, and citations in the analysis',
        backstory="A meticulous editor who ensures 100% accuracy and proper citations.",
        verbose=True,
        allow_delegation=False,
        tools=[citation_checker_tool],
        llm=llm
    )
