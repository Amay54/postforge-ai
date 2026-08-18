import re
from typing import Dict, Any
from app.agents.base import BaseAgent
from app.schemas.agent_schemas import GeneratorOutput, AgentExecutionResult
from app.llm.mock import clean_subject_line, check_prompt_leakage

GENERATOR_SYSTEM_PROMPT = """You are a master LinkedIn copywriter and executive thought leader.
Strict Rules:
1. First 2 lines MUST be high-converting scroll-stoppers (hook).
2. Use clean whitespace, 1-2 sentence paragraphs.
3. Integrate real insights, technical data, and counter-intuitive lessons.
4. End with an open, thought-provoking question to drive comments.
5. Include 3-5 hyper-relevant hashtags at the bottom derived from the domain topic.
6. When feedback from the Reviewer is provided, carefully address every single critique.
7. CRITICAL ANTI-LEAKAGE RULE: NEVER include user instruction meta-phrases (e.g. "Create a LinkedIn post", "Write a post", "Target audience", "Desired tone", "The user requested") in the output text. Write strictly in an authentic, executive first-person practitioner voice.

Return valid JSON adhering to GeneratorOutput schema."""

class GeneratorAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm, "Generator")

    async def run(self, input_data: Dict[str, Any]) -> AgentExecutionResult:
        raw_topic = input_data.get("topic", "")
        cleaned_topic = clean_subject_line(raw_topic)
        audience = input_data.get("target_audience", "")
        tone = input_data.get("tone", "")
        objective = input_data.get("content_objective", "")
        plan = input_data.get("plan", {})
        research = input_data.get("research", {})
        feedback = input_data.get("feedback")
        iteration = input_data.get("iteration", 1)
        current_post = input_data.get("current_post")

        user_prompt = f"""Core Topic: {cleaned_topic}
Target Audience: {audience}
Desired Tone: {tone}
Content Objective: {objective}
Plan: {plan}
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
        
        # Post-generation anti-leakage sanitizer
        if isinstance(res.content, dict) and "post_text" in res.content:
            post_text = res.content["post_text"]
            leaks = check_prompt_leakage(post_text)
            for leak in leaks:
                post_text = re.sub(re.escape(leak), "", post_text, flags=re.IGNORECASE)
            res.content["post_text"] = post_text.strip()
            
        return res
