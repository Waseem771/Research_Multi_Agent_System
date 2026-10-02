from crewai import Agent

def get_fact_checker(llm):
    return Agent(
        role='Rigorous Fact Checker',
        goal='Verify all claims, data points, and citations in the analysis',
        backstory="""A meticulous editor who ensures 100% accuracy and proper citations.
        You carefully read the analyst's report and verify each claim using your own knowledge.
        You do NOT need external tools — you rely on your critical reasoning to spot errors.""",
        verbose=True,
        allow_delegation=False,
        tools=[],  # No tools — prevents Groq JSON parse failure on large inputs
        llm=llm
    )
