from typing import Dict, Any
from app.agents.base import BaseAgent
from app.schemas.agent_schemas import PlannerOutput, AgentExecutionResult

PLANNER_SYSTEM_PROMPT = """You are an elite LinkedIn Editorial Director and Viral Content Strategist.
Given the user objective, target audience, and desired tone:
1. Deconstruct the core hook angle.
2. Outline key narrative beats for LinkedIn engagement.
3. Identify target audience pain points.
4. Specify whether external domain research/citations are required.
5. Provide actionable direction for the Generator.

Return valid JSON adhering to PlannerOutput schema."""

class PlannerAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm, "Planner")

    async def run(self, input_data: Dict[str, Any]) -> AgentExecutionResult:
        topic = input_data.get("topic", "")
        tone = input_data.get("tone", "thought-provoking")
        audience = input_data.get("target_audience", "Tech Leaders & Engineers")
        objective = input_data.get("content_objective", "Thought Leadership")
        
        user_prompt = f"""Content Objective: {objective}
Topic: {topic}
Target Audience: {audience}
Desired Tone: {tone}

Create a complete LinkedIn content strategy plan."""

        res = await self.llm.generate(
            prompt=user_prompt,
            system_prompt=PLANNER_SYSTEM_PROMPT,
            response_schema=PlannerOutput,
            temperature=0.4
        )
        res.agent_name = self.name
        return res
