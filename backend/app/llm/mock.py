import time
from typing import Type, TypeVar, Optional
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
        
        # 1. Planner Output
        if response_schema == PlannerOutput or "content strategy plan" in prompt.lower():
            content = PlannerOutput(
                hook_angle="Most enterprise AI teams are optimizing the wrong latency bottleneck.",
                target_audience_pains=[
                    "High token cost for continuous fine-tuning",
                    "Parametric hallucination in domain workflows",
                    "Slow retrieval latency in multi-hop QA"
                ],
                narrative_beats=[
                    "The counter-intuitive industry shift: RAG > Fine-Tuning for fast iteration",
                    "Real architecture teardown: hybrid dense/sparse vector indexing",
                    "3 concrete production lessons learned after 1M queries",
                    "The actionable takeaway for engineering leaders"
                ],
                requires_research=True,
                research_queries=["RAG hallucination mitigation benchmarks 2026", "Vector search vs fine-tuning costs"],
                key_takeaway="Don't fine-tune what you can ground with high-precision retrieval."
            ).model_dump()
            
        # 2. Generator Output
        elif response_schema == GeneratorOutput or "candidate linkedin post" not in prompt.lower() and "reviewer feedback" in prompt.lower() or "draft" in prompt.lower():
            post_content = """Stop fine-tuning your LLMs for domain knowledge. It's a $100k mistake.

85% of engineering leaders we interviewed last quarter admitted their fine-tuned models hallucinated within 30 days of production launch.

Here is why:
Model weights are frozen in time. Your enterprise knowledge is not.

When we switched our architecture to Hybrid RAG (Dense + BM25 with cross-encoder re-ranking):
? Hallucinations dropped by 92%
? Knowledge ingestion time dropped from 3 days to 4 minutes
? Inference compute costs dropped by 78%

The 3 rules every AI Architect must enforce:
1. Ground truth belongs in indexed storage, not static weights.
2. Chunk size is not a one-size-fits-all: use parent-document retrieval.
3. Track groundedness metrics in real-time, not just cosine similarity.

Are you still fine-tuning for factual retrieval, or have you made the switch to dynamic RAG?

#ArtificialIntelligence #MachineLearning #SystemArchitecture #GenerativeAI #SoftwareEngineering"""
            
            content = GeneratorOutput(
                post_text=post_content,
                hook="Stop fine-tuning your LLMs for domain knowledge. It's a $100k mistake.",
                call_to_action="Are you still fine-tuning for factual retrieval, or have you made the switch to dynamic RAG?",
                hashtags=["#ArtificialIntelligence", "#MachineLearning", "#SystemArchitecture", "#GenerativeAI", "#SoftwareEngineering"],
                word_count=len(post_content.split()),
                character_count=len(post_content)
            ).model_dump()
            
        # 3. Reviewer Output
        elif response_schema == ReviewerOutput or "critique strictly" in prompt.lower() or "candidate linkedin post to evaluate" in prompt.lower():
            # Check iteration
            is_iter_1 = "iteration: 1" in prompt.lower()
            if is_iter_1:
                overall = 78
                approved = False
                issues = [
                    "Hook could create higher contrast tension.",
                    "First section needs more granular benchmark numbers."
                ]
                feedback = "Great structure, but the opening hook needs higher shock value and sharper engineering metrics."
                instructions = [
                    "Start with a direct bold claim contrasting cost vs performance.",
                    "Add explicit percentage improvements for hallucination reduction."
                ]
                scores = ReviewScores(
                    hook_impact=75,
                    storytelling=80,
                    professional_depth=82,
                    clarity=85,
                    engagement_potential=76,
                    originality=78,
                    structure=84,
                    actionability=79,
                    emotional_resonance=72,
                    authenticity=79
                )
            else:
                overall = 91
                approved = True
                issues = []
                feedback = "Outstanding post. The hook is provocative, the architecture insights are concrete, and formatting is mobile-optimized."
                instructions = []
                scores = ReviewScores(
                    hook_impact=92,
                    storytelling=89,
                    professional_depth=94,
                    clarity=93,
                    engagement_potential=90,
                    originality=88,
                    structure=95,
                    actionability=91,
                    emotional_resonance=86,
                    authenticity=92
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
