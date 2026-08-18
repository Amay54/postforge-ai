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

PROMPT_LEAKAGE_PATTERNS = [
    r"create\s+(?:a\s+)?linkedin\s+post",
    r"write\s+(?:a\s+)?linkedin\s+post",
    r"generate\s+(?:a\s+)?linkedin\s+post",
    r"target\s+audience",
    r"desired\s+tone",
    r"quality\s+threshold",
    r"max\s+iterations",
    r"the\s+user\s+asked",
    r"your\s+prompt",
    r"as\s+requested",
    r"here\s+is\s+(?:a|the)\s+post",
    r"in\s+this\s+post\s+i\s+will"
]

def check_prompt_leakage(text: str) -> List[str]:
    """Returns list of leaked prompt phrases found in text."""
    found = []
    text_lower = text.lower()
    for pat in PROMPT_LEAKAGE_PATTERNS:
        match = re.search(pat, text_lower)
        if match:
            found.append(match.group(0))
    return found

def clean_subject_line(raw_text: str) -> str:
    """Strips meta-instructions from user input to get the true semantic topic."""
    text = raw_text.strip()
    topic_match = re.search(r'(?:Topic|topic):\s*([^\n]+)', text)
    if topic_match:
        text = topic_match.group(1).strip()
    else:
        text = text.split('\n')[0].strip()

    prefix_patterns = [
        r'^(?:please\s+)?(?:create|write|generate|craft|make|draft|produce)\s+(?:a\s+)?(?:high-converting\s+|viral\s+|compelling\s+|professional\s+)?(?:linkedin\s+)?(?:post|article|update|content|thought\s+leadership)?\s*(?:about|on|explaining|discussing|breaking\s+down|covering|regarding|detailing|for)?\s*',
        r'^(?:explain|describe|break\s+down|analyze|discuss|give\s+me|show)\s+(?:why|how|what|the)?\s*',
        r'^(?:why|how|what)\s+'
    ]
    for p in prefix_patterns:
        text = re.sub(p, '', text, flags=re.IGNORECASE).strip()
        
    text = re.sub(r'(?:Target audience|Desired tone|Content objective|Keep it concise|Use a professional).*', '', text, flags=re.IGNORECASE).strip()
    text = re.sub(r'[\.\?!,;:]+$', '', text).strip()
    return text if len(text) > 3 else raw_text.strip()

def _extract_topic_and_keywords(prompt_text: str) -> dict:
    """Extract topic, audience, and key concepts from the input prompt string."""
    cleaned_topic = clean_subject_line(prompt_text)
    subject_lower = cleaned_topic.lower()
    
    # 1. Agentic AI Systems / PostForge AI Pipeline
    if any(k in subject_lower for k in ["agent", "agentic", "postforge", "multi-agent", "workflow", "planner", "reviewer", "approval", "human-in-the-loop"]):
        return {
            "topic": "Building an Autonomous Agentic AI System for LinkedIn Publishing with Human-in-the-Loop Approval",
            "hook": "Most AI content tools treat generation as a one-shot prompt. Autonomous agentic systems require stateful verification.",
            "hook_iter2": "Most AI automation fails in production because it relies on raw, unverified one-shot generations. Here is how we engineered an autonomous, multi-agent pipeline with rigorous quality guardrails:",
            "pains": [
                "Single-prompt LLMs producing generic, unverified hallucinations",
                "Lack of automated multi-dimensional rubric scoring before publishing",
                "Uncontrolled API side-effects without Human-in-the-Loop governance"
            ],
            "beats": [
                "The core engineering shift: from static prompt chains to stateful multi-agent state machines",
                "The 6-stage architecture: Planner ? Researcher ? Generator ? Reviewer ? Iterative Refinement ? Human-in-the-Loop Approval",
                "Production governance: 10-dimensional weighted quality evaluation and live LinkedIn REST API publishing",
                "Thoughtful discussion question on agentic orchestration"
            ],
            "body_iter1": """Most AI content tools treat generation as a one-shot prompt. Autonomous agentic systems require stateful verification.

When building PostForge AI, we decoupled monolithic generation into a coordinated multi-agent workflow:

1. Planner Agent: Deconstructs the core user topic into target audience pain points and narrative beats.
2. Researcher Agent: Retrieves grounding facts and domain benchmarks.
3. Generator Agent: Synthesizes high-impact drafts optimized for mobile feed readability.
4. Reviewer Agent: Rigorously scores the draft across 10 editorial dimensions (Hook, Depth, Clarity, Actionability).
5. Iterative Refinement Loop: Automatically refines the post until it surpasses the 85+ quality threshold.
6. Human-in-the-Loop Approval: Protects brand safety by requiring explicit human authorization before live LinkedIn dispatch.

The result: High-density, authentic engineering insights without hallucinations or prompt leakage.

How is your engineering team implementing verification guardrails in multi-agent workflows?

#ArtificialIntelligence #MachineLearning #SystemArchitecture #SoftwareEngineering #AgenticAI""",
            "body_iter2": """Most AI automation fails in production because it relies on raw, unverified one-shot generations. Here is how we engineered an autonomous, multi-agent pipeline with rigorous quality guardrails:

Rather than trusting a single LLM output, PostForge AI runs an iterative LangGraph state machine designed for enterprise reliability:

The 6-Stage Architecture:

1. Planner Agent
Breaks raw prompts into audience pain points, narrative arcs, and research requirements.

2. Researcher Agent
Gathers verified domain facts to prevent hallucinated claims.

3. Generator Agent
Drafts crisp, high-value posts optimized for mobile feeds and substantive takeaways.

4. Reviewer Agent (10-Dimensional Rubric)
Objectively evaluates Hook Impact (15%), Clarity (12%), Professional Depth (12%), and Actionability (10%).

5. Autonomous Refinement Loop
If the weighted score is below 85, actionable feedback is fed back into the Generator for automated revision.

6. Human-in-the-Loop Governance
Final publishing to LinkedIn's official REST API occurs ONLY after explicit user review and approval.

Key takeaway: Autonomous agents are powerful, but reliable evaluation guardrails are what make them production-ready.

How is your engineering team structuring automated quality gates in agentic AI architectures?

#ArtificialIntelligence #MachineLearning #SystemArchitecture #SoftwareEngineering #AgenticAI""",
            "hashtags": ["#ArtificialIntelligence", "#MachineLearning", "#SystemArchitecture", "#SoftwareEngineering", "#AgenticAI"],
            "cta": "How is your engineering team structuring automated quality gates in agentic AI architectures?"
        }

    # 2. AI Prototype to Production Failures
    elif ("prototype" in subject_lower and "production" in subject_lower) or ("fail" in subject_lower and "ai" in subject_lower):
        return {
            "topic": "Why Enterprise AI Projects Fail Moving from Prototype to Production",
            "hook": "80% of enterprise AI prototypes never survive the transition to production.",
            "hook_iter2": "Most AI prototypes look brilliant in Jupyter notebooks. In production, they fail within weeks. Here is the actual reason why:",
            "pains": [
                "Silent data drift and schema mismatch under live production loads",
                "Unpredictable latency spikes and exploding inference API costs",
                "Lack of automated grounding gates and continuous evaluation pipelines"
            ],
            "beats": [
                "The fundamental gap: benchmark accuracy vs production resilience",
                "3 critical failure modes: Data distribution drift, Cost/latency compound curves, and Missing feedback telemetry",
                "Actionable architectural blueprint: MLOps grounding, automated regression gates, and canary rollouts",
                "Discussion prompt for engineering leaders"
            ],
            "body_iter1": """80% of enterprise AI prototypes never survive the transition to production.

The reason isn't the underlying model ? it's the operational scaffolding around it.

When transitioning AI from proof-of-concept to production, teams hit 3 major failure points:

1. Silent Data Drift: Real user prompts look nothing like synthetic test datasets. Unmonitored models degrade quietly without throwing errors.
2. Latency & Token Economics: Multi-step LLM chains that work in demos become cost-prohibitive under concurrent enterprise traffic.
3. Lack of Automated Evaluation: Without continuous quality guardrails, hallucination regressions slip into customer workflows undetected.

How high-performing engineering teams bridge the gap:
? Build continuous evaluation gates before deploying model updates.
? Decouple monolithic prompt chains into discrete, cached micro-services.
? Log end-to-end token latency telemetry alongside standard system metrics.

What is the biggest operational hurdle your team has faced when moving AI into production?

#ArtificialIntelligence #MachineLearning #MLOps #SystemDesign #SoftwareEngineering #TechLeadership""",
            "body_iter2": """Most AI prototypes look brilliant in Jupyter notebooks. In production, they fail within weeks. Here is the actual reason why:

A demo only needs to work once for an executive sponsor. Production requires working reliably 100,000 times a day under noisy real-world conditions.

The 3 Core Production Killers and How to Solve Them:

1. Data Drift & Schema Fragility
? The Flaw: Unstructured user inputs violate assumptions baked into prompt templates.
? The Fix: Implement schema validation and deterministic input sanitize filters at the API boundary.

2. Cost & Latency Compounding
? The Flaw: Synchronous multi-agent chains cause user wait times to exceed 8 seconds.
? The Fix: Cache intermediate embeddings, stream token outputs, and use tiered model routing (small models for classification, large models for synthesis).

3. Missing Quality Guardrails
? The Flaw: Relying on manual ad-hoc testing instead of automated evaluation datasets.
? The Fix: Enforce automated rubric scoring before any generation reaches the user.

Production takeaway: Model capability is a commodity. Operational reliability is your competitive advantage.

What has been your team's single most effective practice for keeping AI reliable in production?

#ArtificialIntelligence #MachineLearning #MLOps #SystemDesign #SoftwareEngineering #TechLeadership""",
            "hashtags": ["#ArtificialIntelligence", "#MachineLearning", "#MLOps", "#SystemDesign", "#SoftwareEngineering", "#TechLeadership"],
            "cta": "What has been your team's single most effective practice for keeping AI reliable in production?"
        }

    # 3. Python / Recursion
    elif "recursion" in subject_lower or ("python" in subject_lower and "rag" not in subject_lower and "ai" not in subject_lower):
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

    # 4. RAG / Retrieval
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

    # 5. Generic Clean Topic
    else:
        words = [w.capitalize() for w in re.findall(r'\b[A-Za-z]{3,}\b', cleaned_topic)[:4]]
        topic_title = " ".join(words) if words else "Engineering Excellence"
        
        return {
            "topic": topic_title,
            "hook": f"The biggest misconception about {topic_title.lower()} is that speed comes at the cost of stability.",
            "hook_iter2": f"If you want to master {topic_title.lower()}, stop optimizing for surface metrics and focus on fundamentals:",
            "pains": [
                f"Lack of clear framework when executing {topic_title.lower()}",
                "Overcomplicating architectures before establishing reliable feedback loops",
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
            "hashtags": [f"#{w}" for w in words] + ["#TechLeadership", "#SoftwareEngineering"],
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
        
        is_iter_1 = bool(re.search(r'iteration[\s_:]*1(?!\d)', prompt.lower()))
        is_iter_2_plus = bool(re.search(r'iteration[\s_:]*[2-9]', prompt.lower()))
        has_feedback = "reviewer feedback" in prompt.lower() or "previous draft" in prompt.lower() or is_iter_2_plus
        
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
                
            # Quality Gate: Ensure ZERO prompt leakage exists in output
            leaks = check_prompt_leakage(post_content)
            for leak in leaks:
                post_content = re.sub(re.escape(leak), "", post_content, flags=re.IGNORECASE)
            
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
            # Extract candidate post text from prompt
            post_match = re.search(r'Candidate LinkedIn Post to Evaluate:\s*(?:"""|\'\'\')?\s*(.*?)\s*(?:"""|\'\'\'|Critique strictly|$)', prompt, re.DOTALL)
            candidate_text = post_match.group(1).strip() if post_match else prompt
            
            # Check for genuine prompt leakage in the candidate post itself
            leaks = check_prompt_leakage(candidate_text)
            
            if leaks:
                scores = ReviewScores(
                    hook_impact=45,
                    clarity=55,
                    professional_depth=50,
                    engagement_potential=48,
                    originality=45,
                    actionability=50,
                    structure=55,
                    storytelling=45,
                    authenticity=40,
                    emotional_resonance=45
                )
                math_overall = calculate_weighted_overall_score(scores)
                issues = [f"Critical Prompt Leakage detected: '{', '.join(leaks)}'."]
                feedback = "Draft contains raw prompt leakage meta-instructions. Strip meta-phrases and write in an authentic executive first-person voice."
                instructions = [
                    "Remove all meta-instruction phrases such as 'create a linkedin post' or 'target audience'.",
                    "Synthesize the narrative naturally around the core topic.",
                    "Strengthen the opening hook to be direct and insight-driven."
                ]
            elif is_iter_1 or not has_feedback:
                # Iteration 1 draft: Solid baseline (78) needing hook tension and formatting polish
                scores = ReviewScores(
                    hook_impact=76,
                    clarity=82,
                    professional_depth=80,
                    engagement_potential=78,
                    originality=77,
                    actionability=79,
                    structure=78,
                    storytelling=77,
                    authenticity=80,
                    emotional_resonance=75
                )
                math_overall = calculate_weighted_overall_score(scores)
                issues = [
                    "Opening hook could provide sharper contrast and tension before the 'see more' cutoff.",
                    "Architecture section would benefit from numbered distinct stages for mobile scanning."
                ]
                feedback = f"Strong conceptual foundation for {topic_info['topic']}. To exceed 85+, sharpen the opening hook's tension and structure the architectural stages with clear visual spacing."
                instructions = [
                    "Open with a high-contrast statement about why naive implementations fail in production.",
                    "Format the key architectural stages into distinct numbered blocks.",
                    "Ensure the ending question invites high-intent practitioner discussions."
                ]
            else:
                # Iteration 2+ revised draft: Exceptional polished post (91-92)
                scores = ReviewScores(
                    hook_impact=93,
                    clarity=92,
                    professional_depth=92,
                    engagement_potential=90,
                    originality=89,
                    actionability=91,
                    structure=94,
                    storytelling=90,
                    authenticity=91,
                    emotional_resonance=86
                )
                math_overall = calculate_weighted_overall_score(scores)
                issues = []
                feedback = f"Exceptional revised post for {topic_info['topic']}. The opening hook is compelling, the architectural stages are crisp and actionable, and formatting is optimized for mobile feeds."
                instructions = []
                
            content = ReviewerOutput(
                dimension_scores=scores,
                overall_score=math_overall,
                approved=(math_overall >= 85),
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
