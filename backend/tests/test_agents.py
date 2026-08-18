import pytest
from app.llm.mock import MockLLMService
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.generator import GeneratorAgent
from app.agents.reviewer import ReviewerAgent

@pytest.mark.asyncio
async def test_planner_agent():
    llm = MockLLMService()
    planner = PlannerAgent(llm)
    res = await planner.run({
        "topic": "Why RAG is transforming enterprise search",
        "tone": "thought-provoking",
        "target_audience": "AI Engineers",
        "content_objective": "Thought Leadership"
    })
    assert res.agent_name == "Planner"
    assert "hook_angle" in res.content
    assert "narrative_beats" in res.content
    assert isinstance(res.content["narrative_beats"], list)
    assert res.content["requires_research"] is True

@pytest.mark.asyncio
async def test_researcher_agent():
    llm = MockLLMService()
    researcher = ResearcherAgent(llm)
    res = await researcher.run({
        "topic": "Enterprise RAG Architecture",
        "research_queries": ["RAG hallucination benchmarks"]
    })
    assert res.agent_name == "Researcher"
    assert "findings" in res.content
    assert len(res.content["findings"]) >= 1
    assert "claim" in res.content["findings"][0]

@pytest.mark.asyncio
async def test_generator_agent():
    llm = MockLLMService()
    generator = GeneratorAgent(llm)
    res = await generator.run({
        "plan": {"hook_angle": "Most teams build RAG wrong."},
        "iteration": 1
    })
    assert res.agent_name == "Generator"
    assert "post_text" in res.content
    assert "hook" in res.content
    assert len(res.content["post_text"]) > 50

@pytest.mark.asyncio
async def test_reviewer_agent_scores_and_dimensions():
    llm = MockLLMService()
    reviewer = ReviewerAgent(llm)
    res = await reviewer.run({
        "post_text": "Sample candidate LinkedIn post text with data points.",
        "quality_threshold": 85,
        "iteration": 1
    })
    assert res.agent_name == "Reviewer"
    content = res.content
    assert "overall_score" in content
    assert "dimension_scores" in content
    assert "hook_impact" in content["dimension_scores"]
    assert "storytelling" in content["dimension_scores"]
    assert "professional_depth" in content["dimension_scores"]
    assert "clarity" in content["dimension_scores"]
    assert "authenticity" in content["dimension_scores"]
    assert "feedback" in content
    # Invariant: Reviewer MUST NOT rewrite post text directly
    assert "post_text" not in content
