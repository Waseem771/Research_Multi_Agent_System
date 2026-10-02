from crewai import Crew, Process, Task
from config import get_fast_llm, get_power_llm, get_safe_llm
from agents.orchestrator import get_orchestrator
from agents.researcher import get_researcher
from agents.literature_reviewer import get_literature_reviewer
from agents.analyst import get_analyst
from agents.fact_checker import get_fact_checker

def run_research_system(topic: str):
    # ---------------------------------------------------------------
    # Assign models based on task complexity:
    #
    #   openai/gpt-oss-20b          → Researcher, Lit Reviewer  (fast tool calls)
    #   openai/gpt-oss-120b         → Analyst, Orchestrator     (deep reasoning & writing)
    #   openai/gpt-oss-safeguard-20b → Fact Checker             (safety-tuned verification)
    # ---------------------------------------------------------------
    fast_llm  = get_fast_llm()   # openai/gpt-oss-20b
    power_llm = get_power_llm()  # openai/gpt-oss-120b
    safe_llm  = get_safe_llm()   # openai/gpt-oss-safeguard-20b

    researcher   = get_researcher(fast_llm)        # 🕵️ gpt-oss-20b
    lit_reviewer = get_literature_reviewer(fast_llm) # 📚 gpt-oss-20b
    analyst      = get_analyst(power_llm)          # 📊 gpt-oss-120b
    fact_checker = get_fact_checker(safe_llm)      # 🔍 gpt-oss-safeguard-20b
    orchestrator = get_orchestrator(power_llm)     # 👔 gpt-oss-120b

    research_task = Task(
        description=f"Search the web for key facts about: {topic}. Return a concise bullet-point summary (max 300 words).",
        expected_output="Concise bullet-point summary of web findings (max 300 words).",
        agent=researcher
    )

    lit_review_task = Task(
        description=f"Find 2-3 key academic papers about: {topic}. Summarize each in 2 sentences.",
        expected_output="2-3 academic paper summaries (max 200 words total).",
        agent=lit_reviewer
    )

    analysis_task = Task(
        description=f"Using the research and literature summaries, write a structured analysis of: {topic}. Keep it under 400 words.",
        expected_output="Structured analysis under 400 words with key themes and insights.",
        agent=analyst
    )

    fact_check_task = Task(
        description="Review the analysis above. Flag any questionable claims in 3-5 bullet points. Keep it under 200 words.",
        expected_output="Bullet-point fact-check notes under 200 words.",
        agent=fact_checker
    )

    synthesis_task = Task(
        description=f"Write a final Markdown report on '{topic}' using all prior summaries. Include: Executive Summary, Key Findings, Conclusion. Max 500 words.",
        expected_output="A polished Markdown report with Executive Summary, Key Findings, and Conclusion (max 500 words).",
        agent=orchestrator
    )

    crew = Crew(
        agents=[researcher, lit_reviewer, analyst, fact_checker, orchestrator],
        tasks=[research_task, lit_review_task, analysis_task, fact_check_task, synthesis_task],
        process=Process.sequential,
        verbose=True
    )

    return crew.kickoff()
