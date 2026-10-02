from crewai import Crew, Process, Task
from config import get_llm
from agents.orchestrator import get_orchestrator
from agents.researcher import get_researcher
from agents.literature_reviewer import get_literature_reviewer
from agents.analyst import get_analyst
from agents.fact_checker import get_fact_checker

def run_research_system(topic: str):
    llm = get_llm()
    
    researcher = get_researcher(llm)
    lit_reviewer = get_literature_reviewer(llm)
    analyst = get_analyst(llm)
    fact_checker = get_fact_checker(llm)
    orchestrator = get_orchestrator(llm)
    
    # Tasks are defined directly in the coordinator to match the requested structure without a tasks folder
    research_task = Task(
        description=f"Search the web for the latest information on: {topic}",
        expected_output="A summary of the latest web findings.",
        agent=researcher
    )
    
    lit_review_task = Task(
        description=f"Find academic papers related to: {topic}",
        expected_output="A summary of academic literature.",
        agent=lit_reviewer
    )
    
    analysis_task = Task(
        description=f"Analyze the gathered web and academic data for: {topic}",
        expected_output="A structured analytical report.",
        agent=analyst
    )
    
    fact_check_task = Task(
        description="Verify all facts and citations in the analytical report.",
        expected_output="A verified and corrected final report.",
        agent=fact_checker
    )
    
    synthesis_task = Task(
        description="Synthesize the verified report into a polished final document.",
        expected_output="The final, comprehensive research document.",
        agent=orchestrator
    )
    
    crew = Crew(
        agents=[researcher, lit_reviewer, analyst, fact_checker, orchestrator],
        tasks=[research_task, lit_review_task, analysis_task, fact_check_task, synthesis_task],
        process=Process.sequential,
        verbose=True
    )
    
    return crew.kickoff()
