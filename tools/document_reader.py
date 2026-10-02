from crewai.tools import tool

@tool("Document Reader")
def document_reader_tool(file_path: str) -> str:
    """Read contents from a local document."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading document: {e}"
