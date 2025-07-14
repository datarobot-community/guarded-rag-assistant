# Copyright 2024 DataRobot, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import annotations

import json
import time
import traceback
from dataclasses import dataclass
from typing import Any, Dict, List, Union

from langchain.schema import AIMessage, BaseMessage, HumanMessage
from langchain.schema.runnable import Runnable
from langchain_community.callbacks import get_openai_callback
from langchain_core.documents import Document
from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion import Choice


@dataclass
class CitationInfo:
    content: str
    source: str
    page: str


def create_chat_completion(
    response: str,
    model_name: str,
    citations: list[Document],
    created_time: int | None = None,
) -> ChatCompletion:
    """Convert LangChain response to OpenAI ChatCompletion format"""
    if created_time is None:
        created_time = int(time.time())

    choice = Choice(
        finish_reason="stop",
        index=0,
        message={"role": "assistant", "content": response},
    )

    completion = ChatCompletion(
        id=f"chat-{int(time.time())}",
        choices=[choice],
        created=created_time,
        model=model_name,
        object="chat.completion",
        system_fingerprint=None,
    )

    citations_dr = [
        {
            "content": c.page_content,
            "link": c.metadata["source"],
            "metadata": c.metadata,
        }
        for c in citations
    ]

    completion.citations = citations_dr  # type: ignore[attr-defined]
    return completion


def convert_messages_to_chat_history(
    messages: List[Dict[str, str]],
) -> list[Union[HumanMessage, AIMessage]]:
    """Convert OpenAI message format to LangChain chat history format."""
    chat_history: list[Union[HumanMessage, AIMessage]] = []

    # Skip the system message if present and convert other messages
    for msg in messages:
        if msg["role"] == "system":
            continue
        elif msg["role"] == "user":
            chat_history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            chat_history.append(AIMessage(content=msg["content"]))

    # Return all but the last user message (which will be the input)
    if chat_history and isinstance(chat_history[-1], HumanMessage):
        return chat_history[:-1]
    return chat_history


def merge_result_dicts(results: list[dict[str, list[Any]]]) -> dict[str, list[Any]]:
    """Merge multiple result dictionaries into one."""
    final_result: dict[str, list[Any]] = {}

    for result in results:
        for key, values in result.items():
            if key not in final_result:
                final_result[key] = []
            final_result[key].extend(values)

    return final_result


def create_result_dict(
    answer: str, citations: list[CitationInfo], target_column_name: str
) -> dict[str, list[str]]:
    """Create the result dictionary with answer and citations."""
    result = {target_column_name: [answer]}

    for i, citation in enumerate(citations):
        result[f"CITATION_CONTENT_{i}"] = [citation.content]
        result[f"CITATION_SOURCE_{i}"] = [citation.source]
        result[f"CITATION_PAGE_{i}"] = [citation.page]

    return result


def process_citations(chain_output: Dict[str, Any]) -> List[CitationInfo]:
    """Extract citation information from chain output."""
    citations = []
    for doc in chain_output.get("context", []):
        citations.append(
            CitationInfo(
                content=doc.page_content,
                source=doc.metadata.get("source", ""),
                page=doc.metadata.get("page", ""),
            )
        )
    return citations


def process_single_row(
    question: str,
    chat_history: List[BaseMessage],
    chain: Runnable[dict[str, Any], Any],
    target_column_name: str,
) -> dict[str, list[Any]]:
    """Process a single row of data."""
    try:
        with get_openai_callback():
            chain_output = chain.invoke(
                {
                    "input": question,
                    "chat_history": chat_history,
                }
            )

        citations = process_citations(chain_output)
        return create_result_dict(
            answer=chain_output["answer"],
            citations=citations,
            target_column_name=target_column_name,
        )

    except Exception:
        return {target_column_name: [traceback.format_exc()]}


def parse_chat_history(messages_json: str) -> List[BaseMessage]:
    """Convert JSON messages to LangChain message objects."""
    if not messages_json:
        return []

    messages = json.loads(messages_json)
    return [
        HumanMessage.validate(msg) if msg["role"] == "user" else AIMessage.validate(msg)
        for msg in messages
    ]
