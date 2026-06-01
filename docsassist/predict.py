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

import logging
from dataclasses import dataclass

import datarobot as dr
from datarobot.models.deployment.deployment import Deployment
from openai import OpenAI
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from openai.types.chat.chat_completion_user_message_param import (
    ChatCompletionUserMessageParam,
)
from pydantic import ValidationError

from docsassist.deployments import RAGDeployment  # noqa: E402
from docsassist.schema import RAGOutput  # noqa: E402

logger = logging.getLogger(__name__)

# Lazy-loaded deployment ID
_rag_deployment_id = None


def _get_rag_deployment_id() -> str:
    """Get the RAG deployment ID, initializing it if needed."""
    global _rag_deployment_id
    if _rag_deployment_id is None:
        try:
            _rag_deployment_id = RAGDeployment().id
        except ValidationError as e:
            raise ValueError(
                (
                    "Unable to load DataRobot deployment ids. If running locally, verify you have selected "
                    "the correct stack and that it is active using `pulumi stack output`. "
                    "If running in DataRobot, verify your runtime parameters have been set correctly."
                )
            ) from e
    return _rag_deployment_id


@dataclass
class DeploymentInfo:
    deployment: Deployment
    target_name: str


def get_rag_completion(
    question: str,
    messages: list[ChatCompletionMessageParam],
    deployment_id: str | None = None,
    metadata_filter: dict[str, str] | None = None,
) -> RAGOutput:
    """Retrieve predictions from a DataRobot RAG deployment and DataRobot guard deployment

    Args:
        question: The user's question/prompt
        messages: Chat history
        deployment_id: Optional deployment ID (uses environment variable if not provided)
        metadata_filter: Optional metadata filters to apply to vector database retrieval.
                        Multiple filters are combined with AND logic.
                        Example: {"source": "doc.txt", "category": "technical"}

    Returns:
        RAGOutput with completion text and citations
    """
    # Use provided deployment_id or get from environment
    if deployment_id is None:
        deployment_id = _get_rag_deployment_id()

    dr_client = dr.client.get_client()
    openai_client = OpenAI(
        base_url=f"{dr_client.endpoint.rstrip('/')}/deployments/{deployment_id}",
        api_key=dr_client.token,
    )

    # Build request parameters with metadata filter if provided
    if metadata_filter:
        logger.info(f"Applying metadata filters: {metadata_filter}")
        response = openai_client.chat.completions.create(
            model="datarobot-deployed-llm",
            messages=messages
            + [ChatCompletionUserMessageParam(content=question, role="user")],
            extra_body={"metadata_filter": metadata_filter},
        )
    else:
        response = openai_client.chat.completions.create(
            model="datarobot-deployed-llm",
            messages=messages
            + [ChatCompletionUserMessageParam(content=question, role="user")],
        )

    content = response.choices[0].message.content
    logger.info(
        "RAG completion: deployment=%s empty=%s citations=%d",
        deployment_id,
        not content,
        len(getattr(response, "citations", [])),
    )

    return RAGOutput(
        completion=str(content),
        references=getattr(response, "citations", []),
        question=question,
    )
