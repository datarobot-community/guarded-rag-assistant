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

import base64
import logging
import os
import sys

import datarobot as dr
import streamlit as st
from openai.types.chat.chat_completion_assistant_message_param import (
    ChatCompletionAssistantMessageParam,
)
from openai.types.chat.chat_completion_user_message_param import (
    ChatCompletionUserMessageParam,
)
from settings import app_settings
from streamlit.delta_generator import DeltaGenerator
from streamlit_theme import st_theme

sys.path.append("../")
from docsassist import predict
from docsassist.i18n import gettext
from docsassist.schema import (
    RAGOutput,
)

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)


DATAROBOT_ENDPOINT = os.getenv("DATAROBOT_ENDPOINT")
DATAROBOT_API_KEY = os.getenv("DATAROBOT_API_TOKEN")

st.set_page_config(
    page_title=app_settings.page_title, page_icon="./datarobot_favicon.png"
)

with open("./style.css") as f:
    css = f.read()

theme = st_theme()
logo = "./DataRobot_white.svg"
if theme and theme.get("base") == "light":
    logo = "./DataRobot_black.svg"

with open(logo) as f:
    svg = f.read()

st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

dr.Client(endpoint=DATAROBOT_ENDPOINT, token=DATAROBOT_API_KEY)


if "messages" not in st.session_state:
    st.session_state.messages = []

if "response" not in st.session_state:
    st.session_state.response = {}


def render_svg(svg: str) -> None:
    """Renders the given svg string."""
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
    st.write(html, unsafe_allow_html=True)


def render_message(
    container: DeltaGenerator, message: str, is_user: bool = False
) -> None:
    message_role = "user" if is_user else "ai"
    message_label = gettext("User") if is_user else gettext("Assistant")
    container.markdown(
        f"""
    <div class="chat-message {message_role}-message">
        <div class="message-content">
            <span class="message-label"><b>{message_label}:</b></span>
            <span class="message-text">{message}</span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_conversation_history(container: DeltaGenerator) -> None:
    container.subheader(gettext("Conversation History"))
    for message in st.session_state.messages[:-1]:  # Exclude the latest message
        render_message(container, message["content"], message["role"] == "user")
    st.markdown("---")


def render_answer_and_citations(container: DeltaGenerator, response: RAGOutput) -> None:
    render_message(container, response.completion, is_user=False)

    with st.expander(gettext("Show Citations")):
        for i, doc in enumerate(response.references):
            st.markdown(gettext("**Reference {0}:**").format(i + 1))
            st.markdown(gettext("**Source:** {0}").format(doc.metadata["source"]))
            st.markdown(gettext("**Content:**"))
            for text in doc.content.split("\\n"):
                if text.strip():
                    st.markdown(text)
            st.markdown("---")


def main() -> None:
    render_svg(svg)
    st.title(app_settings.page_title)

    chat_container = st.container()
    prompt_container = st.container()
    if st.session_state.messages:
        render_conversation_history(chat_container)
    answer_and_citations_placeholder = chat_container.container()
    if "prompt_sent" not in st.session_state:
        st.session_state.prompt_sent = False
    prompt = prompt_container.chat_input(
        placeholder=gettext("Your message"),
        key=None,
        max_chars=None,
        disabled=False,
        on_submit=None,
        args=None,
        kwargs=None,
    )

    if prompt and prompt.strip():
        st.session_state.prompt_sent = True
        render_message(chat_container, prompt, True)
        with st.spinner(gettext("Getting AI response...")):
            response = predict.get_rag_completion(
                question=prompt,
                messages=st.session_state.messages,
            )
        st.session_state.response = response
        st.session_state.messages.extend(
            [
                ChatCompletionUserMessageParam(content=prompt, role="user"),
                ChatCompletionAssistantMessageParam(
                    content=response.completion, role="assistant"
                ),
            ]
        )

        st.rerun()

    if st.session_state.prompt_sent:
        render_answer_and_citations(
            answer_and_citations_placeholder,
            st.session_state.response,
        )


if __name__ == "__main__":
    main()
