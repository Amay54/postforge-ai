from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.llm.base import BaseLLMService
from app.schemas.agent_schemas import AgentExecutionResult

class BaseAgent(ABC):
    def __init__(self, llm: BaseLLMService, name: str):
        self.llm = llm
        self.name = name

    @abstractmethod
    async def run(self, input_data: Dict[str, Any]) -> AgentExecutionResult:
        pass
