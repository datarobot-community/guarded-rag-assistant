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

# mypy: ignore-errors
import os
import sys
from collections.abc import Iterator
from typing import Union

import pandas as pd
import yaml
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import (
    create_history_aware_retriever,
)
from langchain.chains.retrieval import create_retrieval_chain
from langchain.schema.runnable import Runnable
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_huggingface import (
    HuggingFaceEmbeddings,
)
from langchain_openai import AzureChatOpenAI
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
    CompletionCreateParams,
)

from utils import (
    convert_messages_to_chat_history,
    create_chat_completion,
    merge_result_dicts,
    parse_chat_history,
    process_single_row,
)

sys.path.append("../")

from docsassist.credentials import AzureOpenAICredentials
from docsassist.schema import PROMPT_COLUMN_NAME, TARGET_COLUMN_NAME, RAGModelSettings


def get_chain(
    input_dir, credentials: AzureOpenAICredentials, model_settings: RAGModelSettings
):
    """Instantiate the RAG chain."""
    embedding_function = HuggingFaceEmbeddings(
        model_name=model_settings.embedding_model_name,
        cache_folder=input_dir + "/sentencetransformers",
    )
    db = FAISS.load_local(
        folder_path=input_dir + "/faiss_db",
        embeddings=embedding_function,
        allow_dangerous_deserialization=True,
    )

    llm = AzureChatOpenAI(
        deployment_name=credentials.azure_deployment,
        azure_endpoint=credentials.azure_endpoint,
        openai_api_version=credentials.api_version,
        openai_api_key=credentials.api_key,
        model_name=credentials.azure_deployment,
        temperature=model_settings.temperature,
        verbose=True,
        max_retries=model_settings.max_retries,
        request_timeout=model_settings.request_timeout,
    )
    retriever = VectorStoreRetriever(
        vectorstore=db,
    )
    system_template = model_settings.stuff_prompt
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, just "
        "reformulate it if needed and otherwise return it as is."
    )
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    # Answer question
    qa_system_prompt = system_template
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    # Below we use create_stuff_documents_chain to feed all retrieved context
    # into the LLM. Note that we can also use StuffDocumentsChain and other
    # instances of BaseCombineDocumentsChain.
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    return rag_chain


def load_model(input_dir):
    """Load vector database and prepare chain."""
    with open(os.path.join(input_dir, RAGModelSettings.filename())) as f:
        model_settings = RAGModelSettings.model_validate(yaml.safe_load(f))
    credentials = AzureOpenAICredentials()
    chain = get_chain(input_dir, credentials=credentials, model_settings=model_settings)
    return chain


def score(data: pd.DataFrame, model: Runnable, **kwargs) -> pd.DataFrame:
    """
    Orchestrate a RAG completion with our vector database.

    Args:
        data: Input DataFrame containing questions and optional message history
        model: LangChain chain
        **kwargs: Additional arguments

    Returns:
        DataFrame with answers and citations
    """
    chain = model
    results = []

    for _, row in data.iterrows():
        question = row[PROMPT_COLUMN_NAME]
        chat_history = parse_chat_history(row.get("messages", ""))
        result = process_single_row(
            question, chat_history, chain, target_column_name=TARGET_COLUMN_NAME
        )
        results.append(result)

    final_result = merge_result_dicts(results)
    return pd.DataFrame(final_result)


def chat(
    completion_params: CompletionCreateParams,
    model: Runnable,
) -> Union[ChatCompletion, Iterator[ChatCompletionChunk]]:
    """
    OpenAI-compatible chat function that uses a LangChain RAG chain under the hood.

    Args:
        completion_params: OpenAI-style completion parameters
        model: LangChain chain

    Returns:
        ChatCompletion or Iterator[ChatCompletionChunk]
    """
    chain = model

    # Extract messages from completion params
    messages = completion_params.get("messages", [])

    # Convert messages to chat history
    chat_history = convert_messages_to_chat_history(messages)

    # Get the last user message
    user_message = next(
        (msg["content"] for msg in reversed(messages) if msg["role"] == "user"), None
    )

    if user_message is None:
        raise ValueError("No user message found in completion params")

    # Run the chain with chat history
    response = chain.invoke({"input": user_message, "chat_history": chat_history})

    return create_chat_completion(
        response["answer"],
        completion_params.get("model"),
        citations=response["context"],
    )
