import os
import json
import time
import logging
from typing import Type, TypeVar, Optional
from pydantic import BaseModel

from app.config import settings
from app.llm.base import BaseLLMService
from app.schemas.agent_schemas import AgentExecutionResult

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)

class GeminiLLMService(BaseLLMService):
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_schema: Optional[Type[T]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> AgentExecutionResult:
        t0 = time.time()
        
        try:
            try:
                import google.generativeai as genai
                if self.api_key:
                    genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel(self.model_name)
                
                generation_config = {
                    "temperature": temperature,
                    "max_output_tokens": max_tokens
                }
                
                if response_schema:
                    generation_config["response_mime_type"] = "application/json"
                    enriched_prompt = f"{prompt}\n\nReturn strictly JSON conforming to this schema:\n{response_schema.model_json_schema()}"
                else:
                    enriched_prompt = prompt

                full_prompt = f"{system_prompt}\n\n{enriched_prompt}" if system_prompt else enriched_prompt

                response = await model.generate_content_async(
                    full_prompt,
                    generation_config=generation_config
                )
                raw_text = response.text
                latency = int((time.time() - t0) * 1000)
                
                if response_schema:
                    parsed_json = json.loads(raw_text)
                    valid_obj = response_schema.model_validate(parsed_json)
                    content = valid_obj.model_dump()
                else:
                    content = {"text": raw_text}

                return AgentExecutionResult(
                    agent_name="GeminiLLM",
                    content=content,
                    latency_ms=latency,
                    tokens_prompt=len(full_prompt.split()) * 2,
                    tokens_completion=len(raw_text.split()) * 2,
                    model_name=self.model_name
                )
            except Exception as inner_e:
                logger.warning(f"Live Gemini API unavailable, falling back to mock: {inner_e}")
                from app.llm.mock import MockLLMService
                return await MockLLMService().generate(prompt, system_prompt, response_schema, temperature, max_tokens)
        except Exception as e:
            logger.error(f"LLM execution error: {e}")
            from app.llm.mock import MockLLMService
            return await MockLLMService().generate(prompt, system_prompt, response_schema, temperature, max_tokens)
