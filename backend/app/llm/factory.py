from app.config import settings
from app.llm.base import BaseLLMService
from app.llm.gemini import GeminiLLMService
from app.llm.mock import MockLLMService

def get_llm_service() -> BaseLLMService:
    if settings.MOCK_LLM or not settings.GEMINI_API_KEY:
        return MockLLMService()
    return GeminiLLMService()
