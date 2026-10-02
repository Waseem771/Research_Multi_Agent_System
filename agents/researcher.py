from crewai import Agent
from tools.web_search import web_search_tool

def get_researcher(llm):
    return Agent(
        role='Lead Web Researcher',
        goal='Gather up-to-date general information from the web',
        backstory="A seasoned internet researcher who finds accurate information quickly.",
        verbose=True,
        allow_delegation=False,
        tools=[web_search_tool],
        llm=llm
    )
