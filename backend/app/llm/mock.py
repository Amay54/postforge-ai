import time
import re
from typing import Type, TypeVar, Optional, List
from pydantic import BaseModel

from app.llm.base import BaseLLMService
from app.schemas.agent_schemas import (
    PlannerOutput,
    GeneratorOutput,
    ReviewerOutput,
    ReviewScores,
    AgentExecutionResult
)

T = TypeVar("T", bound=BaseModel)

def _extract_topic_and_keywords(prompt_text: str) -> dict:
    """Extract topic, audience, and key concepts from the input prompt string."""
    # Look for explicit Topic: line first
    topic_match = re.search(r'(?:Topic|topic):\s*(.+)', prompt_text)
    if topic_match:
        target_subject = topic_match.group(1).strip()
    else:
        # Fallback to first line or whole prompt
        target_subject = prompt_text.split('\n')[0].strip()

    subject_lower = target_subject.lower()
    full_lower = prompt_text.lower()
    
    # Check for Python / Recursion
    if "recursion" in subject_lower or ("python" in subject_lower and "rag" not in subject_lower):
        return {
            "topic": "Mastering Recursion in Python for Beginners",
            "hook": "Recursion isn't difficult ? the way it's usually taught is.",
            "hook_iter2": "Most junior developers fear recursion until they understand call stack frames. Here is the mental model:",
            "pains": [
                "Confusion about base cases causing infinite loops / stack overflow",
                "Difficulty visualizing the call stack unwind phase",
                "Unnecessary recursive calls leading to exponential O(2^N) time complexity"
            ],
            "beats": [
                "The mental shift: viewing recursion as stack frames rather than loops",
                "The 3 immutable rules: Base case first, Trust the recursive step, Pass smaller input",
                "Concrete Python example: Fibonacci naive vs memoized @lru_cache",
                "Key takeaway and discussion prompt"
            ],
            "body_iter1": """Recursion isn't difficult ? the way it's usually taught is.

When learning recursion in Python, most engineers hit a wall because they try to trace every branch mentally.

Here is the 3-step blueprint to write clean recursive functions:

1. Define the Base Case First: Always declare the stopping condition at line 1. Without it, you hit `RecursionError: maximum recursion depth exceeded`.
2. Move Toward the Base Case: Every recursive call MUST receive a strictly smaller sub-problem (`n - 1`, `arr[1:]`).
3. Trust the Return Value: Don't trace the entire tree in your head. Assume the recursive call returns the correct sub-result.

Pro Tip: Always use `functools.lru_cache` or dynamic programming when recursive calls overlap.

How did you first build intuition for recursive algorithms?

#Python #SoftwareEngineering #DataStructures #Programming #CodingTips""",
            "body_iter2": """Most junior developers fear recursion until they understand call stack frames. Here is the mental model:

When a function calls itself, Python pauses the current frame and pushes a new frame onto the call stack. It doesn't 'loop' ? it builds a stack of pending promises.

The 3 Golden Rules of Recursion:

1. The Exit Door (Base Case)
Every recursive function must stop itself at the top:
`if n <= 1: return n`

2. The Shrinking Step
Each recursive invocation must operate on a strictly reduced slice of data (`n - 1`).

3. The Unwind (Combine Phase)
The magic happens when the base case is reached and the stack resolves backwards.

Remember: If your recursion branches repeatedly, add Python's built-in `@lru_cache` to transform O(2^N) exponential time into O(N) linear performance.

Which concept was harder for you when starting out: recursion or pointer memory?

#Python #SoftwareEngineering #DataStructures #Programming #ComputerScience""",
            "hashtags": ["#Python", "#SoftwareEngineering", "#DataStructures", "#Programming", "#ComputerScience"],
            "cta": "Which concept was harder for you when starting out: recursion or pointer memory?"
        }

    # Check for RAG / Retrieval
    elif "rag" in subject_lower or "retrieval" in subject_lower or "vector" in subject_lower:
        return {
            "topic": "Deploying RAG Systems in Production",
            "hook": "Deploying RAG to production is 10% vector search and 90% edge-case engineering.",
            "hook_iter2": "Most enterprise RAG architectures fail within 60 days of production launch. Here is why:",
            "pains": [
                "Retrieval noise and low chunk relevancy in dense embeddings",
                "Silent hallucination and grounding drift on domain queries",
                "Multi-hop latency and high token consumption costs"
            ],
            "beats": [
                "The core engineering challenge: naive cosine similarity vs real retrieval precision",
                "3 production-tested fixes: Hybrid Search (BM25 + Dense), Cross-Encoder Re-ranking, and Parent Document Retrieval",
                "Production impact: 92% hallucination reduction and sub-200ms latency",
                "Key takeaway and discussion question for technical leaders"
            ],
            "body_iter1": """Deploying RAG to production is 10% vector search and 90% edge-case engineering.

When scaling Retrieval-Augmented Generation beyond prototype demos, enterprise teams hit 3 major hurdles:

1. Retrieval Quality: Standard cosine similarity returns noisy chunks. Dense vector search alone misses exact keyword identifiers.
2. Grounding Drift: LLMs hallucinate answers when retrieved contexts are ambiguous or partially relevant.
3. Latency & Cost: Multi-hop retrieval queries compound token overhead and slow down response streams.

Practical solutions from production systems:
? Implement Hybrid Retrieval: Combine Dense Vector Search with BM25 keyword matching using Reciprocal Rank Fusion (RRF).
? Use Cross-Encoder Re-Ranking: Filter top-50 retrieved candidates down to top-5 high-relevance chunks before passing to the generator.
? Dynamic Chunking: Decouple small search embeddings from large parent text documents.

What is the biggest operational challenge your team has faced when moving RAG to production?

#GenerativeAI #ArtificialIntelligence #MachineLearning #SystemArchitecture #SoftwareEngineering""",
            "body_iter2": """Most enterprise RAG architectures fail within 60 days of production launch. Here is why:

Naive semantic search works wonders in prototypes, but real enterprise data breaks naive chunking.

Here are the 3 production bottlenecks and how to solve them:

1. Retrieval Precision & Noise
? Challenge: Dense embeddings struggle with exact part numbers, acronyms, and schema IDs.
? Solution: Deploy Hybrid Search combining Dense Vectors + BM25 keyword scoring with Cross-Encoder re-ranking.

2. Hallucination & Grounding Drift
? Challenge: Context stuffing causes LLMs to ignore contradictory retrieved facts.
? Solution: Enforce strict citations and ground-truth validation filters before output synthesis.

3. Latency & Cost Overhead
? Challenge: Naive multi-vector queries triple token usage and latency.
? Solution: Use Parent-Document Retrieval ? embed small sentence-level chunks for search, but retrieve parent document blocks for context.

Production takeaway: Ground truth belongs in structured indexing, not static model assumptions.

What has been your team's biggest operational breakthrough in scaling RAG systems?

#ArtificialIntelligence #MachineLearning #SystemArchitecture #GenerativeAI #SoftwareEngineering""",
            "hashtags": ["#ArtificialIntelligence", "#MachineLearning", "#SystemArchitecture", "#GenerativeAI", "#SoftwareEngineering"],
            "cta": "What has been your team's biggest operational breakthrough in scaling RAG systems?"
        }

    # Generic Custom Topic Synthesis
    else:
        words = [w.capitalize() for w in re.findall(r'\b[A-Za-z]{3,}\b', target_subject)[:4]]
        topic_title = " ".join(words) if words else "Engineering Excellence"
        
        return {
            "topic": topic_title,
            "hook": f"The biggest misconception about {topic_title.lower()} is that speed comes at the cost of stability.",
            "hook_iter2": f"If you want to master {topic_title.lower()}, stop optimizing for surface metrics and focus on fundamentals:",
            "pains": [
                f"Lack of clear framework when executing {topic_title.lower()}",
                "Overcomplicating architectures before finding product-market fit",
                "Communication silos between engineering and technical leadership"
            ],
            "beats": [
                f"The core principle behind successful {topic_title.lower()}",
                "3 actionable lessons learned across enterprise production systems",
                "Practical implementation guidelines for high-performing engineering teams",
                "Discussion question for the community"
            ],
            "body_iter1": f"""The biggest misconception about {topic_title.lower()} is that speed comes at the cost of stability.

After analyzing high-performing technical organizations, the top 3 patterns always emerge:

1. Clarify the Core Constraint: Before adding complexity, isolate the single bottleneck in your workflow.
2. Automate the Quality Gate: Human review works best when backed by automated validation pipelines.
3. Measure What Matters: Focus on outcome metrics rather than vanity activity.

Building resilient systems requires disciplined execution and clear architectural boundaries.

What is the most critical principle you follow in {topic_title.lower()}?

#TechLeadership #SoftwareEngineering #Architecture #Innovation #EngineeringExcellence""",
            "body_iter2": f"""If you want to master {topic_title.lower()}, stop optimizing for surface metrics and focus on fundamentals:

High-velocity engineering teams don't move faster by taking shortcuts. They move faster because they build reliable feedback loops.

The 3 Key Pillars:

1. Radical Clarity on Requirements
Every architecture decision should start with the user problem, not the latest framework trend.

2. Shorten the Iteration Loop
The faster you can test, review, and iterate, the lower the risk of failure in production.

3. Embed Quality at Every Stage
Automated validation + explicit human oversight ensures high standards without slowing down delivery.

What is the single most valuable lesson you have learned about {topic_title.lower()}?

#TechLeadership #SoftwareEngineering #SystemDesign #Innovation #ProductDevelopment""",
            "hashtags": ["#TechLeadership", "#SoftwareEngineering", "#SystemDesign", "#Innovation", "#ProductDevelopment"],
            "cta": f"What is the single most valuable lesson you have learned about {topic_title.lower()}?"
        }


class MockLLMService(BaseLLMService):
    def __init__(self, model_name: str = "mock-gemini-2.5-flash"):
        self.model_name = model_name

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_schema: Optional[Type[T]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> AgentExecutionResult:
        t0 = time.time()
        topic_info = _extract_topic_and_keywords(prompt)
        
        is_iter_1 = "iteration: 1" in prompt.lower() or "iteration 1" in prompt.lower() or "iteration_number: 1" in prompt.lower()
        has_feedback = "reviewer feedback" in prompt.lower() or "previous draft" in prompt.lower()
        
        # 1. Planner Output
        if response_schema == PlannerOutput or "content strategy plan" in prompt.lower():
            content = PlannerOutput(
                hook_angle=topic_info["hook"],
                target_audience_pains=topic_info["pains"],
                narrative_beats=topic_info["beats"],
                requires_research=True,
                research_queries=[
                    f"{topic_info['topic']} best practices 2026",
                    f"{topic_info['topic']} architecture patterns"
                ],
                key_takeaway=f"Focus on foundational principles and robust iteration when tackling {topic_info['topic'].lower()}."
            ).model_dump()
            
        # 2. Generator Output
        elif response_schema == GeneratorOutput or ("candidate linkedin post" not in prompt.lower() and ("reviewer feedback" in prompt.lower() or "draft" in prompt.lower() or "plan" in prompt.lower())):
            # Pick iteration 1 vs iteration 2 body
            if has_feedback and not is_iter_1:
                post_content = topic_info["body_iter2"]
                hook_text = topic_info["hook_iter2"]
            else:
                post_content = topic_info["body_iter1"]
                hook_text = topic_info["hook"]
            
            content = GeneratorOutput(
                post_text=post_content,
                hook=hook_text,
                call_to_action=topic_info["cta"],
                hashtags=topic_info["hashtags"],
                word_count=len(post_content.split()),
                character_count=len(post_content)
            ).model_dump()
            
        # 3. Reviewer Output
        elif response_schema == ReviewerOutput or "critique strictly" in prompt.lower() or "candidate linkedin post to evaluate" in prompt.lower():
            if is_iter_1 or not has_feedback:
                overall = 78
                approved = False
                issues = [
                    "Opening hook could provide sharper contrast and punchier tension.",
                    "Middle section needs more explicit bulleted architecture solutions."
                ]
                feedback = f"Solid foundation for {topic_info['topic']}, but the opening hook needs stronger tension and the core solutions should be formatted with clear visual bullets."
                instructions = [
                    "Open with a bold contrast statement about failure modes vs best practices.",
                    "Format the 3 core takeaways with distinct bullet points for mobile readability.",
                    "Strengthen the final question to provoke high-intent practitioner discussion."
                ]
                scores = ReviewScores(
                    hook_impact=76,
                    storytelling=80,
                    professional_depth=81,
                    clarity=84,
                    engagement_potential=77,
                    originality=78,
                    structure=82,
                    actionability=79,
                    emotional_resonance=74,
                    authenticity=79
                )
            else:
                overall = 91
                approved = True
                issues = []
                feedback = f"Exceptional revised post for {topic_info['topic']}. The hook is engaging, technical solutions are crisp and actionable, and formatting is optimized for LinkedIn feeds."
                instructions = []
                scores = ReviewScores(
                    hook_impact=92,
                    storytelling=90,
                    professional_depth=93,
                    clarity=94,
                    engagement_potential=91,
                    originality=89,
                    structure=95,
                    actionability=92,
                    emotional_resonance=86,
                    authenticity=91
                )
                
            content = ReviewerOutput(
                dimension_scores=scores,
                overall_score=overall,
                approved=approved,
                issues=issues,
                feedback=feedback,
                improvement_instructions=instructions
            ).model_dump()
            
        else:
            content = {"message": "Mock generation executed successfully."}

        latency = int((time.time() - t0) * 1000)
        return AgentExecutionResult(
            agent_name="MockLLM",
            content=content,
            latency_ms=max(latency, 80),
            tokens_prompt=len(prompt.split()) * 2,
            tokens_completion=250,
            model_name=self.model_name
        )
