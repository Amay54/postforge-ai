from typing import Dict, Any
from app.agents.base import BaseAgent
from app.services.research import get_research_provider
from app.schemas.agent_schemas import ResearchOutput, AgentExecutionResult

class ResearcherAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm, "Researcher")
        self.provider = get_research_provider()

    async def run(self, input_data: Dict[str, Any]) -> AgentExecutionResult:
        queries = input_data.get("research_queries", [])
        topic = input_data.get("topic", "")
        query = queries[0] if queries else topic
        
        output: ResearchOutput = await self.provider.search(query, max_sources=3)
        return AgentExecutionResult(
            agent_name=self.name,
            content=output.model_dump(),
            latency_ms=120,
            tokens_prompt=50,
            tokens_completion=150,
            model_name="search-provider"
        )
