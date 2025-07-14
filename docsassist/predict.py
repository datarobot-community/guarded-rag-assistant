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
from docsassist.schema import (  # noqa: E402
    RAGOutput,
)

logger = logging.getLogger(__name__)

try:
    rag_deployment_id = RAGDeployment().id
except ValidationError as e:
    raise ValueError(
        (
            "Unable to load DataRobot deployment ids. If running locally, verify you have selected "
            "the correct stack and that it is active using `pulumi stack output`. "
            "If running in DataRobot, verify your runtime parameters have been set correctly."
        )
    ) from e


@dataclass
class DeploymentInfo:
    deployment: Deployment
    target_name: str


def get_rag_completion(
    question: str, messages: list[ChatCompletionMessageParam]
) -> RAGOutput:
    """Retrieve predictions from a DataRobot RAG deployment and DataRobot guard deployment"""
    dr_client = dr.client.get_client()
    openai_client = OpenAI(
        base_url=f"{dr_client.endpoint.rstrip('/')}/deployments/{rag_deployment_id}",
        api_key=dr_client.token,
    )

    response = openai_client.chat.completions.create(
        model="datarobot-deployed-llm",
        messages=messages
        + [ChatCompletionUserMessageParam(content=question, role="user")],
    )

    rag_output = RAGOutput(
        completion=str(response.choices[0].message.content),
        references=response.citations,  # type: ignore[attr-defined]
        question=question,
    )

    return rag_output
