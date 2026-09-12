from dataclasses import dataclass
import base64
import json
from typing import Any, Dict, List, Optional, Protocol

from google import genai
from google.genai import types

from app.core.config import Settings
from app.core.exceptions import LLMConfigurationError, LLMProviderError


@dataclass(frozen=True)
class ToolCall:
    call_id: str
    name: str
    arguments: str
    thought_signature: Optional[bytes] = None


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


class GeminiClient:
    def __init__(self, settings: Settings) -> None:
        self.api_key = settings.gemini_api_key
        self.model = settings.gemini_model
        self.client: Optional[genai.Client] = None

    def _get_client(self) -> genai.Client:
        if not self.api_key:
            raise LLMConfigurationError("GEMINI_API_KEY is not configured")
        if self.client is None:
            self.client = genai.Client(api_key=self.api_key)
        return self.client

    @staticmethod
    def _build_tools(tools: List[Dict[str, Any]]) -> List[types.Tool]:
        declarations = []
        for tool in tools:
            function = tool["function"]
            declarations.append(
                types.FunctionDeclaration(
                    name=function["name"],
                    description=function["description"],
                    parameters_json_schema=function["parameters"],
                )
            )
        return [types.Tool(function_declarations=declarations)]

    @staticmethod
    def _build_contents(messages: List[Dict[str, Any]]) -> List[types.Content]:
        contents: List[types.Content] = []
        for message in messages:
            role = message["role"]
            if role == "system":
                continue
            if role == "user":
                contents.append(
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=message["content"])],
                    )
                )
                continue
            if role == "assistant":
                parts = []
                if message.get("content"):
                    parts.append(types.Part.from_text(text=message["content"]))
                for call in message.get("tool_calls", []):
                    function = call["function"]
                    signature = call.get("thought_signature")
                    function_call = types.FunctionCall(
                        id=call["id"],
                        name=function["name"],
                        args=json.loads(function["arguments"]),
                    )
                    parts.append(
                        types.Part(
                            function_call=function_call,
                            thought_signature=(
                                base64.b64decode(signature) if signature else None
                            ),
                        )
                    )
                if parts:
                    contents.append(types.Content(role="model", parts=parts))
                continue
            if role == "tool":
                contents.append(
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_function_response(
                                name=message["name"],
                                response=json.loads(message["content"]),
                            )
                        ],
                    )
                )
        return contents

    def complete(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        tool_choice: str,
    ) -> LLMResult:
        try:
            response = self._get_client().models.generate_content(
                model=self.model,
                contents=self._build_contents(messages),
                config=types.GenerateContentConfig(
                    system_instruction=next(
                        (message["content"] for message in messages if message["role"] == "system"),
                        None,
                    ),
                    tools=self._build_tools(tools),
                    temperature=0,
                    tool_config=types.ToolConfig(
                        function_calling_config=types.FunctionCallingConfig(
                            mode="ANY" if tool_choice == "required" else "AUTO"
                        )
                    ),
                ),
            )
        except Exception as exc:
            raise LLMProviderError("The LLM provider request failed") from exc

        if not response.candidates:
            raise LLMProviderError("The LLM provider returned no candidates")

        candidate = response.candidates[0]
        content = candidate.content
        function_calls = []
        for part in content.parts if content else []:
            if part.function_call is not None:
                function_calls.append((part.function_call, part.thought_signature))
        tool_calls = [
            ToolCall(
                call_id=function_call.id or "gemini-call-%d" % index,
                name=function_call.name,
                arguments=json.dumps(function_call.args or {}),
                thought_signature=thought_signature,
            )
            for index, (function_call, thought_signature) in enumerate(function_calls)
        ]
        assistant_message: Dict[str, Any] = {
            "role": "assistant",
            "content": response.text if not tool_calls else None,
        }
        if tool_calls:
            assistant_message["tool_calls"] = [
                {
                    "id": tool_call.call_id,
                    "type": "function",
                    "function": {
                        "name": tool_call.name,
                        "arguments": tool_call.arguments,
                    },
                        **(
                            {
                                "thought_signature": base64.b64encode(
                                    tool_call.thought_signature
                                ).decode("ascii")
                            }
                            if tool_call.thought_signature
                            else {}
                        ),
                }
                for tool_call in tool_calls
            ]

        return LLMResult(
            content=response.text if not tool_calls else None,
            tool_calls=tool_calls,
            assistant_message=assistant_message,
        )
