from crewai import Crew, Process, Task
from config import get_fast_llm, get_power_llm, get_safe_llm
from agents.orchestrator import get_orchestrator
from agents.researcher import get_researcher
from agents.literature_reviewer import get_literature_reviewer
from agents.analyst import get_analyst
from agents.fact_checker import get_fact_checker

def run_research_system(topic: str):
    # ─────────────────────────────────────────────────────
    # MODEL ASSIGNMENTS
    #   gpt-4.1-nano   → Researcher, Lit Reviewer  (max 200 tokens out)
    #   gpt-5.2        → Analyst, Orchestrator      (max 300 tokens out)
    #   gpt-4.1-mini   → Fact Checker               (max 150 tokens out)
    #
    # TOKEN BUDGET PER RUN (target < 10,000 total)
    #   Researcher    : ~500  tokens  (in+out)
    #   Lit Reviewer  : ~450  tokens  (in+out)
    #   Analyst       : ~950  tokens  (in+out)
    #   Fact Checker  : ~1050 tokens  (in+out)
    #   Orchestrator  : ~1500 tokens  (in+out)
    #   TOTAL EST.    : ~4,450 tokens ✅
    # ─────────────────────────────────────────────────────
    fast_llm  = get_fast_llm()   # gpt-4.1-nano  — 200 max out
    power_llm = get_power_llm()  # gpt-5.2       — 300 max out
    safe_llm  = get_safe_llm()   # gpt-4.1-mini  — 150 max out

    researcher   = get_researcher(fast_llm)
    lit_reviewer = get_literature_reviewer(fast_llm)
    analyst      = get_analyst(power_llm)
    fact_checker = get_fact_checker(safe_llm)
    orchestrator = get_orchestrator(power_llm)

    # ── TASKS: short prompts = fewer input tokens ──────────

    research_task = Task(
        description=(
            f"Topic: {topic}\n"
            "List 5 key facts. Bullet points only. Max 100 words."
        ),
        expected_output="5 bullet points, max 100 words.",
        agent=researcher
    )

    lit_review_task = Task(
        description=(
            f"Topic: {topic}\n"
            "Name 2 relevant papers. One line each. Max 80 words."
        ),
        expected_output="2 paper titles with one-line summary each. Max 80 words.",
        agent=lit_reviewer
    )

    analysis_task = Task(
        description=(
            f"Topic: {topic}\n"
            "Using prior research, write a short analysis. "
            "3 paragraphs max. Max 150 words."
        ),
        expected_output="3-paragraph analysis. Max 150 words.",
        agent=analyst
    )

    fact_check_task = Task(
        description=(
            "Review the analysis above. "
            "Flag up to 3 questionable claims. Bullets only. Max 80 words."
        ),
        expected_output="Up to 3 flagged claims. Max 80 words.",
        agent=fact_checker
    )

    synthesis_task = Task(
        description=(
            f"Write a final report on: {topic}\n"
            "Sections: ## Summary | ## Key Findings | ## Conclusion\n"
            "Max 200 words total. Use markdown."
        ),
        expected_output="Markdown report: Summary, Key Findings, Conclusion. Max 200 words.",
        agent=orchestrator
    )

    crew = Crew(
        agents=[researcher, lit_reviewer, analyst, fact_checker, orchestrator],
        tasks=[research_task, lit_review_task, analysis_task, fact_check_task, synthesis_task],
        process=Process.sequential,
        verbose=True
    )

    return crew.kickoff()
