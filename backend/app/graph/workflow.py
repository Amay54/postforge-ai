import time
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.graph.state import PostGenerationState
from app.graph.routing import should_research, quality_router
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.generator import GeneratorAgent
from app.agents.reviewer import ReviewerAgent
from app.llm.factory import get_llm_service
from app.models.entities import ContentSession, PostRevision, PostReview
from app.services.observability import ObservabilityService

class PostGenerationWorkflow:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm = get_llm_service()
        self.planner = PlannerAgent(self.llm)
        self.researcher = ResearcherAgent(self.llm)
        self.generator = GeneratorAgent(self.llm)
        self.reviewer = ReviewerAgent(self.llm)
        self.app = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(PostGenerationState)

        workflow.add_node("planner", self._planner_node)
        workflow.add_node("researcher", self._researcher_node)
        workflow.add_node("generator", self._generator_node)
        workflow.add_node("reviewer", self._reviewer_node)
        workflow.add_node("human_approval", self._human_approval_node)

        workflow.set_entry_point("planner")

        workflow.add_conditional_edges(
            "planner",
            should_research,
            {
                "researcher": "researcher",
                "generator": "generator"
            }
        )

        workflow.add_edge("researcher", "generator")
        workflow.add_edge("generator", "reviewer")

        workflow.add_conditional_edges(
            "reviewer",
            quality_router,
            {
                "generator": "generator",
                "human_approval": "human_approval"
            }
        )

        workflow.add_edge("human_approval", END)

        return workflow.compile()

    async def _planner_node(self, state: PostGenerationState) -> Dict[str, Any]:
        t0 = time.time()
        res = await self.planner.run({
            "topic": state.topic,
            "tone": state.tone,
            "target_audience": state.target_audience,
            "content_objective": state.content_objective
        })
        plan_dict = res.content
        latency = int((time.time() - t0) * 1000)
        
        await ObservabilityService.log_step(
            db=self.db,
            session_id=state.session_id,
            agent_name="Planner",
            step_number=1,
            raw_output=str(plan_dict),
            model_name=res.model_name,
            tokens_prompt=res.tokens_prompt,
            tokens_completion=res.tokens_completion,
            latency_ms=latency
        )
        
        req_res = plan_dict.get("requires_research", True)
        return {
            "plan": plan_dict,
            "requires_research": req_res,
            "current_step": "planner_completed"
        }

    async def _researcher_node(self, state: PostGenerationState) -> Dict[str, Any]:
        t0 = time.time()
        queries = state.plan.get("research_queries", [state.topic]) if state.plan else [state.topic]
        res = await self.researcher.run({
            "topic": state.topic,
            "research_queries": queries
        })
        research_dict = res.content
        latency = int((time.time() - t0) * 1000)
        
        await ObservabilityService.log_step(
            db=self.db,
            session_id=state.session_id,
            agent_name="Researcher",
            step_number=2,
            raw_output=str(research_dict),
            model_name=res.model_name,
            tokens_prompt=res.tokens_prompt,
            tokens_completion=res.tokens_completion,
            latency_ms=latency
        )
        return {
            "research": research_dict,
            "current_step": "researcher_completed"
        }

    async def _generator_node(self, state: PostGenerationState) -> Dict[str, Any]:
        t0 = time.time()
        new_iteration = state.iteration + 1
        latest_feedback = state.latest_review.get("feedback") if state.latest_review else None
        
        res = await self.generator.run({
            "topic": state.topic,
            "target_audience": state.target_audience,
            "tone": state.tone,
            "content_objective": state.content_objective,
            "plan": state.plan,
            "research": state.research,
            "feedback": latest_feedback,
            "iteration": new_iteration,
            "current_post": state.current_post
        })
        gen_dict = res.content
        latency = int((time.time() - t0) * 1000)
        
        post_text = gen_dict.get("post_text", "")
        hook = gen_dict.get("hook", "")
        hashtags = gen_dict.get("hashtags", [])
        
        # Save Revision to DB
        revision = PostRevision(
            session_id=state.session_id,
            iteration_number=new_iteration,
            content=post_text,
            hook=hook,
            hashtags=hashtags,
            character_count=len(post_text),
            word_count=len(post_text.split()),
            generated_by_model=res.model_name
        )
        self.db.add(revision)
        await self.db.commit()
        await self.db.refresh(revision)
        
        await ObservabilityService.log_step(
            db=self.db,
            session_id=state.session_id,
            agent_name=f"Generator (Iter {new_iteration})",
            step_number=2 + new_iteration * 2 - 1,
            raw_output=post_text,
            model_name=res.model_name,
            tokens_prompt=res.tokens_prompt,
            tokens_completion=res.tokens_completion,
            latency_ms=latency
        )
        
        return {
            "iteration": new_iteration,
            "current_post": post_text,
            "hook": hook,
            "hashtags": hashtags,
            "current_step": f"generator_iter_{new_iteration}"
        }

    async def _reviewer_node(self, state: PostGenerationState) -> Dict[str, Any]:
        t0 = time.time()
        res = await self.reviewer.run({
            "post_text": state.current_post,
            "quality_threshold": state.quality_threshold,
            "iteration": state.iteration
        })
        rev_dict = res.content
        latency = int((time.time() - t0) * 1000)
        
        overall = rev_dict.get("overall_score", 85)
        approved = rev_dict.get("approved", overall >= state.quality_threshold)
        scores = rev_dict.get("dimension_scores", {})
        
        # Get current revision id
        stmt = select(PostRevision).where(
            PostRevision.session_id == state.session_id,
            PostRevision.iteration_number == state.iteration
        )
        res_rev = await self.db.execute(stmt)
        revision = res_rev.scalar_one_or_none()
        rev_id = revision.id if revision else "unknown"
        
        # Save Review to DB
        review_db = PostReview(
            session_id=state.session_id,
            revision_id=rev_id,
            iteration_number=state.iteration,
            overall_score=overall,
            approved=approved,
            score_hook_impact=scores.get("hook_impact", 80),
            score_storytelling=scores.get("storytelling", 80),
            score_professional_depth=scores.get("professional_depth", 80),
            score_clarity=scores.get("clarity", 80),
            score_engagement_potential=scores.get("engagement_potential", 80),
            score_originality=scores.get("originality", 80),
            score_structure=scores.get("structure", 80),
            score_actionability=scores.get("actionability", 80),
            score_emotional_resonance=scores.get("emotional_resonance", 80),
            score_authenticity=scores.get("authenticity", 80),
            identified_flaws=rev_dict.get("issues", []),
            feedback=rev_dict.get("feedback", ""),
            improvement_instructions=rev_dict.get("improvement_instructions", [])
        )
        self.db.add(review_db)
        await self.db.commit()
        
        await ObservabilityService.log_step(
            db=self.db,
            session_id=state.session_id,
            agent_name=f"Reviewer (Iter {state.iteration})",
            step_number=2 + state.iteration * 2,
            raw_output=f"Score: {overall}/100, Approved: {approved}",
            model_name=res.model_name,
            tokens_prompt=res.tokens_prompt,
            tokens_completion=res.tokens_completion,
            latency_ms=latency
        )
        
        new_feedback_history = list(state.feedback_history)
        if rev_dict.get("feedback"):
            new_feedback_history.append(rev_dict["feedback"])
            
        return {
            "latest_review": rev_dict,
            "quality_score": overall,
            "quality_passed": approved,
            "feedback_history": new_feedback_history,
            "current_step": f"reviewer_iter_{state.iteration}"
        }

    async def _human_approval_node(self, state: PostGenerationState) -> Dict[str, Any]:
        # Update ContentSession in DB
        stmt = select(ContentSession).where(ContentSession.id == state.session_id)
        res = await self.db.execute(stmt)
        session = res.scalar_one_or_none()
        if session:
            session.final_post_content = state.current_post
            session.final_quality_score = state.quality_score
            session.iteration_count = state.iteration
            session.status = "awaiting_approval"
            await self.db.commit()
            
        return {
            "status": "awaiting_approval",
            "current_step": "completed"
        }

    async def run(self, initial_state: Dict[str, Any]) -> PostGenerationState:
        state_obj = PostGenerationState(**initial_state)
        result = await self.app.ainvoke(state_obj)
        return PostGenerationState(**result)
