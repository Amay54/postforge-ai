from abc import ABC, abstractmethod
from typing import Type, TypeVar, Optional, Any, Dict
from pydantic import BaseModel
from app.schemas.agent_schemas import AgentExecutionResult

T = TypeVar("T", bound=BaseModel)

class BaseLLMService(ABC):
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_schema: Optional[Type[T]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> AgentExecutionResult:
        pass
