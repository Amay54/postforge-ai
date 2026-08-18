import re
from typing import Dict, Any
from app.agents.base import BaseAgent
from app.schemas.agent_schemas import GeneratorOutput, AgentExecutionResult
from app.llm.mock import clean_subject_line, check_prompt_leakage

GENERATOR_SYSTEM_PROMPT = """You are an elite LinkedIn Copywriter and Technical Thought Leader.

Your goal is to craft high-impact LinkedIn posts that score 85+ across the 10 editorial evaluation dimensions:
1. Hook Impact (15%): Open with a high-tension, curiosity-driven statement (first 2-3 lines before 'see more') that stops the scroll without clickbait.
2. Clarity (12%): Keep sentences tight, crisp, and free of corporate jargon, buzzwords, or filler.
3. Professional Depth (12%): Provide concrete architectural insights, engineering realities, or deep domain expertise.
4. Engagement Potential (12%): End with a thoughtful, open-ended question that prompts meaningful engineering discussions.
5. Originality (10%): Offer unique framing, lessons learned, or counter-intuitive truths rather than generic platitudes.
6. Actionability (10%): Deliver clear, practical takeaways or implementation steps.
7. Structure (8%): Use 1-2 sentence paragraphs, generous whitespace, and clean bulleting for mobile feed readability.
8. Storytelling (8%): Maintain a natural narrative arc from challenge/bottleneck to resolution.
9. Authenticity (7%): Write in a grounded, first-person practitioner voice.
10. Topic-Specific Hashtags: Conclude with 3-5 hyper-relevant technical hashtags.

CRITICAL CONSTRAINTS:
- Do NOT invent fake statistics or claim unverified features.
- Do NOT leak meta-prompts or instructions (e.g. "Create a post", "Target audience", "As requested", "Here is a post").
- Keep total post length within the requested character limits.
- When revising based on Reviewer feedback, directly address every single critique.

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
            text = res.content["post_text"]
            leaks = check_prompt_leakage(text)
            for leak in leaks:
                text = re.sub(re.escape(leak), "", text, flags=re.IGNORECASE).strip()
            res.content["post_text"] = text
            res.content["character_count"] = len(text)
            res.content["word_count"] = len(text.split())

        return res
