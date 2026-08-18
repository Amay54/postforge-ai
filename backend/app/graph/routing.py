from app.graph.state import PostGenerationState

def should_research(state: PostGenerationState) -> str:
    if state.requires_research:
        return "researcher"
    return "generator"

def quality_router(state: PostGenerationState) -> str:
    if state.quality_passed:
        return "human_approval"
    if state.iteration >= state.max_iterations:
        return "human_approval"
    return "generator"
