import json
from typing import Any, Dict, List, Optional, Set

from app.ai.client import LLMClient
from app.ai.prompts import SYSTEM_PROMPT
from app.ai.tools import BackendToolExecutor, TOOL_DEFINITIONS
from app.core.exceptions import ToolExecutionError


class CopilotService:
    def __init__(
        self,
        llm_client: LLMClient,
        tool_executor: BackendToolExecutor,
        max_tool_rounds: int = 4,
    ) -> None:
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_tool_rounds = max_tool_rounds

    def answer(
        self,
        query: str,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]
        messages.extend(history or [])
        messages.append({"role": "user", "content": query})
        tools_used: List[str] = []
        unique_tools: Set[str] = set()

        for round_number in range(self.max_tool_rounds):
            result = self.llm_client.complete(
                messages=messages,
                tools=TOOL_DEFINITIONS,
                tool_choice="required" if round_number == 0 else "auto",
            )

            if not result.tool_calls:
                if not result.content or not result.content.strip():
                    raise ToolExecutionError("The LLM returned an empty answer")
                if not tools_used:
                    raise ToolExecutionError(
                        "The LLM returned an answer without retrieving operational data"
                    )
                return {
                    "answer": result.content.strip(),
                    "tools_used": tools_used,
                    "metadata": {"tool_rounds": round_number + 1},
                }

            messages.append(result.assistant_message)
            for tool_call in result.tool_calls:
                tool_result = self.tool_executor.execute(
                    tool_call.name, tool_call.arguments
                )
                if tool_call.name not in unique_tools:
                    unique_tools.add(tool_call.name)
                    tools_used.append(tool_call.name)
                messages.append(
                    {
                        "role": "tool",
                        "name": tool_call.name,
                        "tool_call_id": tool_call.call_id,
                        "content": json.dumps(tool_result),
                    }
                )

        raise ToolExecutionError("The LLM exceeded the maximum tool-call rounds")
