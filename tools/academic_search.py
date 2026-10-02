from crewai.tools import tool
import urllib.request

@tool("Academic Paper Search")
def academic_search_tool(query: str) -> str:
    """Search for academic papers and literature on a topic."""
    url = f"http://export.arxiv.org/api/query?search_query=all:{query.replace(' ', '+')}&start=0&max_results=3"
    try:
        response = urllib.request.urlopen(url)
        data = response.read().decode('utf-8')
        return f"Academic results for {query}:\n{data[:500]}..."
    except Exception as e:
        return f"Could not fetch academic papers: {e}"
