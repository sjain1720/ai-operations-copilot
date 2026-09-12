from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol

from openai import OpenAI

from app.core.config import Settings
from app.core.exceptions import LLMConfigurationError, LLMProviderError


@dataclass(frozen=True)
class ToolCall:
    call_id: str
    name: str
    arguments: str


@dataclass(frozen=True)
class LLMResult:
    content: Optional[str]
    tool_calls: List[ToolCall]
    assistant_message: Dict[str, Any]


class LLMClient(Protocol):
    def complete(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        tool_choice: str,
    ) -> LLMResult:
        ...


class OpenAIClient:
    def __init__(self, settings: Settings) -> None:
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model
        self.client: Optional[OpenAI] = None

    def complete(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        tool_choice: str,
    ) -> LLMResult:
        if not self.api_key:
            raise LLMConfigurationError("OPENAI_API_KEY is not configured")

        if self.client is None:
            self.client = OpenAI(api_key=self.api_key)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                temperature=0,
            )
        except Exception as exc:
            raise LLMProviderError("The LLM provider request failed") from exc

        if not response.choices:
            raise LLMProviderError("The LLM provider returned no choices")

        message = response.choices[0].message
        tool_calls = [
            ToolCall(
                call_id=tool_call.id,
                name=tool_call.function.name,
                arguments=tool_call.function.arguments,
            )
            for tool_call in (message.tool_calls or [])
        ]
        assistant_message: Dict[str, Any] = {
            "role": "assistant",
            "content": message.content,
        }
        if tool_calls:
            assistant_message["tool_calls"] = [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                }
                for tool_call in (message.tool_calls or [])
            ]

        return LLMResult(
            content=message.content,
            tool_calls=tool_calls,
            assistant_message=assistant_message,
        )
