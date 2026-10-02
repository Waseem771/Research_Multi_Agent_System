from langchain_community.tools import DuckDuckGoSearchRun
from crewai.tools import tool

@tool("DuckDuckGo Web Search")
def web_search_tool(search_query: str) -> str:
    """Search the web for general information on a given topic."""
    return DuckDuckGoSearchRun().run(search_query)
