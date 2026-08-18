from typing import Dict, Any
from app.agents.base import BaseAgent
from app.schemas.agent_schemas import ReviewerOutput, AgentExecutionResult

REVIEWER_SYSTEM_PROMPT = """You are a ruthless LinkedIn Content Evaluator and Editorial Critic.
CRITICAL CONSTRAINT: You evaluate and score posts across 10 precise dimensions (0-100 scale). You do NOT rewrite or output new post text directly. You provide analytical critiques, identified flaws, and concrete directives for the Generator agent.

The 10 Dimensions:
1. hook_impact (0-100): Scroll-stopping power of the first 2 lines.
2. storytelling (0-100): Narrative arc and human perspective.
3. professional_depth (0-100): Domain expertise and substantive insight.
4. clarity (0-100): Precision, absence of fluff and cliches.
5. engagement_potential (0-100): Likelihood of comments, debates, and shares.
6. originality (0-100): Novel perspective vs recycled generic platitudes.
7. structure (0-100): Line breaks, readability, mobile formatting.
8. actionability (0-100): Tangible takeaway for the reader.
9. emotional_resonance (0-100): Empathy, vulnerability, or inspiring energy.
10. authenticity (0-100): Genuine human voice vs sterile AI boilerplate.

Overall score is the weighted average of all 10 dimensions.
Approved is true ONLY if overall_score >= quality_threshold.

Return valid JSON adhering to ReviewerOutput schema."""

class ReviewerAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm, "Reviewer")

    async def run(self, input_data: Dict[str, Any]) -> AgentExecutionResult:
        post_text = input_data.get("post_text", "")
        threshold = input_data.get("quality_threshold", 85)
        iteration = input_data.get("iteration", 1)

        user_prompt = f"""Quality Threshold: {threshold}
Iteration: {iteration}

Candidate LinkedIn Post to Evaluate:
\"\"\"
{post_text}
\"\"\"

Critique strictly against all 10 dimensions. Calculate overall_score and provide detailed improvement instructions."""

        res = await self.llm.generate(
            prompt=user_prompt,
            system_prompt=REVIEWER_SYSTEM_PROMPT,
            response_schema=ReviewerOutput,
            temperature=0.2
        )
        res.agent_name = self.name
        return res
