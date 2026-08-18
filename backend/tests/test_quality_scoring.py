import pytest
from app.agents.reviewer import ReviewerAgent, calculate_weighted_overall_score, DIMENSION_WEIGHTS
from app.agents.generator import GeneratorAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.schemas.agent_schemas import ReviewScores
from app.llm.mock import MockLLMService

def test_reviewer_10_dimensional_mathematical_weights():
    """Verify that dimension weights sum to exactly 1.0 (100%) and produce exact scores."""
    total_weight = sum(DIMENSION_WEIGHTS.values())
    assert abs(total_weight - 1.0) < 1e-6, f"Dimension weights must sum to 1.0, got {total_weight}"

    # Test baseline calculation
    scores = ReviewScores(
        hook_impact=90,          # 90 * 0.15 = 13.5
        clarity=90,              # 90 * 0.12 = 10.8
        professional_depth=90,   # 90 * 0.12 = 10.8
        engagement_potential=90, # 90 * 0.12 = 10.8
        originality=90,          # 90 * 0.10 = 9.0
        actionability=90,        # 90 * 0.10 = 9.0
        structure=90,            # 90 * 0.08 = 7.2
        storytelling=90,         # 90 * 0.08 = 7.2
        authenticity=90,         # 90 * 0.07 = 6.3
        emotional_resonance=90   # 90 * 0.06 = 5.4
    )
    overall = calculate_weighted_overall_score(scores)
    assert overall == 90

@pytest.mark.asyncio
async def test_weak_post_with_prompt_leakage_scores_low():
    """Verify that a generic post containing prompt leakage receives low score (<60) and is not approved."""
    llm = MockLLMService()
    reviewer = ReviewerAgent(llm)

    weak_post = "Create a LinkedIn post for the target audience. As requested, here is a post with generic advice."
    res = await reviewer.run({
        "post_text": weak_post,
        "quality_threshold": 85,
        "iteration": 1
    })

    content = res.content
    assert content["overall_score"] < 60
    assert content["approved"] is False
    assert len(content["issues"]) > 0
    assert "Prompt Leakage" in content["issues"][0]

@pytest.mark.asyncio
async def test_iterative_refinement_improves_score_from_78_to_90_plus():
    """Verify that Draft #1 scores ~78 with feedback and Revision #2 achieves 85+."""
    llm = MockLLMService()
    generator = GeneratorAgent(llm)
    reviewer = ReviewerAgent(llm)

    topic = "Why Enterprise AI Projects Fail Moving from Prototype to Production"
    
    # 1. Draft 1
    gen1 = await generator.run({
        "topic": topic,
        "iteration": 1
    })
    post1 = gen1.content["post_text"]

    rev1 = await reviewer.run({
        "post_text": post1,
        "quality_threshold": 85,
        "iteration": 1,
        "topic": topic
    })
    score1 = rev1.content["overall_score"]
    assert 70 <= score1 < 85, f"Expected Draft 1 score between 70-84, got {score1}"
    assert rev1.content["approved"] is False
    assert len(rev1.content["improvement_instructions"]) > 0

    # 2. Revision with feedback
    gen2 = await generator.run({
        "topic": topic,
        "current_post": post1,
        "feedback": rev1.content["feedback"],
        "iteration": 2
    })
    post2 = gen2.content["post_text"]

    rev2 = await reviewer.run({
        "post_text": post2,
        "quality_threshold": 85,
        "iteration": 2,
        "topic": topic
    })
    score2 = rev2.content["overall_score"]
    assert score2 >= 85, f"Expected Revision 2 score >= 85, got {score2}"
    assert rev2.content["approved"] is True

@pytest.mark.asyncio
async def test_exact_user_prompt_agentic_post_generation():
    """Verify the exact user prompt produces a high-scoring post with full 10-dimensional review."""
    llm = MockLLMService()
    planner = PlannerAgent(llm)
    researcher = ResearcherAgent(llm)
    generator = GeneratorAgent(llm)
    reviewer = ReviewerAgent(llm)

    user_prompt = (
        "Create a LinkedIn post about how I built an agentic AI system that can plan, research, "
        "generate, review, refine, and publish LinkedIn content with human approval. "
        "Target audience: AI/ML engineers, software engineers, and recruiters. "
        "Explain the architecture briefly: Planner ? Researcher ? Generator ? Reviewer ? "
        "iterative refinement ? Human-in-the-Loop approval ? LinkedIn publishing. "
        "Do not invent statistics or claim features that are not implemented. "
        "Keep it under 1800 characters. End with a thoughtful question."
    )

    # 1. Plan
    plan_res = await planner.run({
        "topic": user_prompt,
        "target_audience": "AI/ML engineers, software engineers, and recruiters",
        "tone": "Thought Leadership"
    })
    assert "hook_angle" in plan_res.content

    # 2. Research
    res_res = await researcher.run({
        "topic": user_prompt,
        "research_queries": plan_res.content.get("research_queries", [])
    })

    # 3. Generate Iteration 1
    gen1 = await generator.run({
        "topic": user_prompt,
        "target_audience": "AI/ML engineers, software engineers, and recruiters",
        "plan": plan_res.content,
        "research": res_res.content,
        "iteration": 1
    })
    post1 = gen1.content["post_text"]

    # 4. Review Iteration 1
    rev1 = await reviewer.run({
        "post_text": post1,
        "quality_threshold": 85,
        "iteration": 1,
        "topic": user_prompt
    })
    assert rev1.content["overall_score"] < 85

    # 5. Revise Iteration 2
    gen2 = await generator.run({
        "topic": user_prompt,
        "target_audience": "AI/ML engineers, software engineers, and recruiters",
        "plan": plan_res.content,
        "research": res_res.content,
        "current_post": post1,
        "feedback": rev1.content["feedback"],
        "iteration": 2
    })
    post2 = gen2.content["post_text"]

    # Character limit assertion
    assert len(post2) < 1800, f"Post length {len(post2)} exceeds 1800 characters!"

    # 6. Review Iteration 2
    rev2 = await reviewer.run({
        "post_text": post2,
        "quality_threshold": 85,
        "iteration": 2,
        "topic": user_prompt
    })
    score2 = rev2.content["overall_score"]
    assert score2 >= 85, f"Revised post score {score2} must be >= 85"
    assert rev2.content["approved"] is True

    # Check 10-dimensional rubric presence
    dims = rev2.content["dimension_scores"]
    for dim_name in DIMENSION_WEIGHTS.keys():
        assert dim_name in dims
        assert dims[dim_name] >= 80

    # Ensure pipeline concepts and ending question are present
    assert "Planner" in post2
    assert "Reviewer" in post2
    assert "?" in gen2.content["call_to_action"]
