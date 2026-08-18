from typing import Dict, Any
from app.agents.base import BaseAgent
from app.schemas.agent_schemas import GeneratorOutput, AgentExecutionResult

GENERATOR_SYSTEM_PROMPT = """You are a master LinkedIn copywriter who creates high-engagement, authentic executive posts.
Rules:
1. First 2 lines MUST be high-converting scroll-stoppers (hook).
2. Use clean whitespace, 1-2 sentence paragraphs.
3. Integrate real insights, data, and counter-intuitive lessons.
4. End with an open, thought-provoking question to drive comments.
5. Include 3-5 hyper-relevant hashtags at the bottom.
6. When feedback from the Reviewer is provided, carefully address every single critique.

Return valid JSON adhering to GeneratorOutput schema."""

class GeneratorAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm, "Generator")

    async def run(self, input_data: Dict[str, Any]) -> AgentExecutionResult:
        plan = input_data.get("plan", {})
        research = input_data.get("research", {})
        feedback = input_data.get("feedback")
        iteration = input_data.get("iteration", 1)
        current_post = input_data.get("current_post")

        user_prompt = f"""Plan: {plan}
Research Findings: {research}
Iteration: {iteration}
"""
        if feedback and current_post:
            user_prompt += f"""
Previous Draft:
{current_post}

Reviewer Feedback to Fix:
{feedback}
"""

        res = await self.llm.generate(
            prompt=user_prompt,
            system_prompt=GENERATOR_SYSTEM_PROMPT,
            response_schema=GeneratorOutput,
            temperature=0.7
        )
        res.agent_name = self.name
        return res
