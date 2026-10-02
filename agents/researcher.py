from crewai import Agent
from tools.web_search import web_search_tool

def get_researcher(llm):
    return Agent(
        role='Lead Web Researcher',
        goal='Gather up-to-date general information from the web on the given topic',
        backstory="""A seasoned internet researcher who finds accurate information quickly.
        You use the web search tool to find the latest data, then summarize your findings concisely.""",
        verbose=True,
        allow_delegation=False,
        tools=[web_search_tool],
        max_iter=3,
        llm=llm
    )
