from typing import Dict, Any
from app.agents.base import BaseAgent
from app.schemas.agent_schemas import ReviewerOutput, ReviewScores, AgentExecutionResult

DIMENSION_WEIGHTS = {
    "hook_impact": 0.15,
    "clarity": 0.12,
    "professional_depth": 0.12,
    "engagement_potential": 0.12,
    "originality": 0.10,
    "actionability": 0.10,
    "structure": 0.08,
    "storytelling": 0.08,
    "authenticity": 0.07,
    "emotional_resonance": 0.06,
}

def calculate_weighted_overall_score(scores: ReviewScores) -> int:
    """Mathematically computes the 10-dimensional weighted quality score."""
    total = (
        scores.hook_impact * DIMENSION_WEIGHTS["hook_impact"] +
        scores.clarity * DIMENSION_WEIGHTS["clarity"] +
        scores.professional_depth * DIMENSION_WEIGHTS["professional_depth"] +
        scores.engagement_potential * DIMENSION_WEIGHTS["engagement_potential"] +
        scores.originality * DIMENSION_WEIGHTS["originality"] +
        scores.actionability * DIMENSION_WEIGHTS["actionability"] +
        scores.structure * DIMENSION_WEIGHTS["structure"] +
        scores.storytelling * DIMENSION_WEIGHTS["storytelling"] +
        scores.authenticity * DIMENSION_WEIGHTS["authenticity"] +
        scores.emotional_resonance * DIMENSION_WEIGHTS["emotional_resonance"]
    )
    return max(0, min(100, round(total)))

REVIEWER_SYSTEM_PROMPT = """You are a rigorous, objective LinkedIn Editorial Director and Quality Evaluator.

CRITICAL ROLE:
You evaluate candidate LinkedIn posts against 10 precise editorial dimensions (0-100 scale), apply strict scoring anchors, and mathematically compute the weighted overall score. You do NOT rewrite the post; you provide analytical critiques, identified flaws, and concrete directives for the Generator agent.

Explicit Scoring Rubrics per Dimension:
- 90?100 (Exceptional): World-class quality, immediately captivating hook, zero fluff, authentic practitioner perspective, razor-sharp takeaways, natural mobile formatting.
- 80?89 (Strong): High quality, clear value, well-formatted, compelling hook, actionable insight.
- 70?79 (Good): Solid foundational content, clear message, but hook could have higher tension or formatting could be punchier.
- 60?69 (Average): Standard generic post, predictable insights, lacks depth or narrative tension.
- 0?59 (Weak): Generic platitudes, sterile corporate AI tone, clickbait, prompt leakage, unsupported claims, poor structure.

The 10 Dimensions & Their Mathematical Weights:
1. hook_impact (15% / 0.15): Scroll-stopping power of the first 2-3 lines before 'see more'. Creates genuine curiosity and professional tension without cheap clickbait.
2. clarity (12% / 0.12): Precision of language, conciseness, absence of buzzwords, corporate jargon, and filler.
3. professional_depth (12% / 0.12): Substantive domain expertise, technical accuracy, architectural insight, or real-world operational truth.
4. engagement_potential (12% / 0.12): Likelihood of inspiring meaningful discussion, thoughtful comments, and practitioner debates via high-value prompts.
5. originality (10% / 0.10): Novel angle, fresh framing, or counter-intuitive practitioner lesson vs recycled cliches.
6. actionability (10% / 0.10): Concrete, implementable takeaways or mental models that the reader can apply immediately.
7. structure (8% / 0.08): 1-2 sentence paragraphs, clean whitespace, mobile readability, crisp bulleting.
8. storytelling (8% / 0.08): Cohesive narrative flow, problem-to-solution transition, relatable human engineering perspective.
9. authenticity (7% / 0.07): Genuine human practitioner voice, humility, grounded experience vs sterile AI boilerplate.
10. emotional_resonance (6% / 0.06): Empathy for developer/practitioner struggles, inspiring and respectful energy.

Mathematical Formula for overall_score:
overall_score = round(
    0.15 * hook_impact +
    0.12 * clarity +
    0.12 * professional_depth +
    0.12 * engagement_potential +
    0.10 * originality +
    0.10 * actionability +
    0.08 * structure +
    0.08 * storytelling +
    0.07 * authenticity +
    0.06 * emotional_resonance
)

Strict Reviewer Rules:
- Never artificially inflate scores for generic formatting (emojis, hashtags, keyword stuffing).
- For any dimension scoring below 80, provide specific, actionable directives in improvement_instructions.
- Check compliance with the user's requested topic, audience, length, and constraints.
- Approved is true ONLY if overall_score >= quality_threshold.

Return valid JSON adhering to ReviewerOutput schema."""

class ReviewerAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm, "Reviewer")

    async def run(self, input_data: Dict[str, Any]) -> AgentExecutionResult:
        post_text = input_data.get("post_text", "")
        threshold = input_data.get("quality_threshold", 85)
        iteration = input_data.get("iteration", 1)
        topic = input_data.get("topic", "")
        target_audience = input_data.get("target_audience", "")

        user_prompt = f"""Quality Threshold: {threshold}
Iteration: {iteration}
Original Request Topic: {topic}
Target Audience: {target_audience}

Candidate LinkedIn Post to Evaluate:
\"\"\"
{post_text}
\"\"\"

Critique strictly against all 10 dimensions. Calculate overall_score mathematically using the exact weights, and provide detailed improvement instructions for any dimension below 80."""

        res = await self.llm.generate(
            prompt=user_prompt,
            system_prompt=REVIEWER_SYSTEM_PROMPT,
            response_schema=ReviewerOutput,
            temperature=0.2
        )
        
        # Ensure mathematical accuracy of overall_score
        if isinstance(res.content, dict) and "dimension_scores" in res.content:
            dim_dict = res.content["dimension_scores"]
            if isinstance(dim_dict, dict):
                scores_obj = ReviewScores(**dim_dict)
                math_overall = calculate_weighted_overall_score(scores_obj)
                res.content["overall_score"] = math_overall
                res.content["approved"] = (math_overall >= threshold)
                
        res.agent_name = self.name
        return res
