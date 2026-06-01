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
from docsassist.schema import RAGOutput, RAGType

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

from telemetry import init_telemetry, span  # noqa: E402

init_telemetry()


DATAROBOT_ENDPOINT = os.getenv("DATAROBOT_ENDPOINT")
DATAROBOT_API_KEY = os.getenv("DATAROBOT_API_TOKEN")
RAG_TYPE = os.getenv("MAIN_RAG_TYPE", "dr").lower()  # Default to 'dr' if not set

st.set_page_config(
    page_title=app_settings.page_title,
    page_icon="./datarobot_favicon.png",
    initial_sidebar_state="auto",  # Auto: expanded on desktop, collapsed on mobile
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
    st.session_state.response = None

if "metadata_filters" not in st.session_state:
    st.session_state.metadata_filters = {}


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


def render_metadata_filters() -> dict[str, str]:
    """Render metadata filter UI in sidebar and return selected filters."""
    with st.sidebar:
        st.subheader("🔍 Metadata Filters")
        st.markdown(
            "Filter documents by metadata. Multiple filters use AND logic (all must match)."
        )

        # Display currently applied filters with individual delete buttons
        if st.session_state.metadata_filters:
            st.markdown("---")
            st.markdown("**Active Filters:**")
            filters_to_remove = []

            for key, value in st.session_state.metadata_filters.items():
                # Use columns to align delete button to the right edge
                col1, col2 = st.columns([0.89, 0.11])
                with col1:
                    st.markdown(f"**{key}:** {value}")
                with col2:
                    if st.button(
                        "❌", key=f"remove_{key}", help=f"Remove {key} filter"
                    ):
                        filters_to_remove.append(key)

            # Remove filters that were marked for deletion
            for key in filters_to_remove:
                del st.session_state.metadata_filters[key]
                st.rerun()

            # Clear all filters button
            if st.button("🗑️ Clear All Filters", use_container_width=True):
                st.session_state.metadata_filters = {}
                st.rerun()
        else:
            st.info("No filters applied. All documents will be searched.")

        st.markdown("---")
        st.markdown("**Add New Filter:**")

        # Source filter (with Enter key support via form)
        with st.form(key="source_filter_form", clear_on_submit=True):
            source_filter = st.text_input(
                "Source",
                value="",
                help="Filter by document source (exact match required)",
                placeholder="e.g., doc.txt",
            )
            submitted_source = st.form_submit_button(
                "➕ Add Source Filter", use_container_width=True
            )
            if submitted_source:
                if source_filter.strip():
                    st.session_state.metadata_filters["source"] = source_filter.strip()
                    st.rerun()
                else:
                    st.warning(
                        "⚠️ Please enter a source value before adding the filter."
                    )

        # Category filter (with Enter key support via form)
        with st.form(key="category_filter_form", clear_on_submit=True):
            category_filter = st.text_input(
                "Category",
                value="",
                help="Filter by document category (exact match required)",
                placeholder="e.g., technical",
            )
            submitted_category = st.form_submit_button(
                "➕ Add Category Filter", use_container_width=True
            )
            if submitted_category:
                if category_filter.strip():
                    st.session_state.metadata_filters["category"] = (
                        category_filter.strip()
                    )
                    st.rerun()
                else:
                    st.warning(
                        "⚠️ Please enter a category value before adding the filter."
                    )

        # Department filter (with Enter key support via form)
        with st.form(key="department_filter_form", clear_on_submit=True):
            department_filter = st.text_input(
                "Department",
                value="",
                help="Filter by department (exact match required)",
                placeholder="e.g., HR",
            )
            submitted_department = st.form_submit_button(
                "➕ Add Department Filter", use_container_width=True
            )
            if submitted_department:
                if department_filter.strip():
                    st.session_state.metadata_filters["department"] = (
                        department_filter.strip()
                    )
                    st.rerun()
                else:
                    st.warning(
                        "⚠️ Please enter a department value before adding the filter."
                    )

        # Year filter with dropdown
        with st.form(key="year_filter_form", clear_on_submit=True):
            year_options = [""] + [str(year) for year in range(2025, 2019, -1)]
            year_filter = st.selectbox(
                "Year",
                options=year_options,
                help="Filter by year",
                index=0,
            )
            submitted_year = st.form_submit_button(
                "➕ Add Year Filter", use_container_width=True
            )
            if submitted_year:
                if year_filter:
                    st.session_state.metadata_filters["year"] = year_filter
                    st.rerun()
                else:
                    st.warning("⚠️ Please select a year before adding the filter.")

        # Add custom metadata field (with Enter key support via form)
        st.markdown("---")
        st.markdown("**Custom Metadata Field:**")
        st.caption(
            "Use this section to add filters for metadata fields not listed above."
        )
        with st.form(key="custom_filter_form", clear_on_submit=True):
            custom_field = st.text_input(
                "Field Name",
                value="",
                help="Enter any custom metadata field name not listed above",
                placeholder="e.g., author, region, language",
            )
            custom_value = st.text_input(
                "Field Value",
                value="",
                help="Enter the value for your custom metadata field",
                placeholder="e.g., John Doe, EMEA, English",
            )
            submitted_custom = st.form_submit_button(
                "➕ Add Custom Filter", use_container_width=True
            )
            if submitted_custom:
                if custom_field.strip() and custom_value.strip():
                    st.session_state.metadata_filters[custom_field.strip()] = (
                        custom_value.strip()
                    )
                    st.rerun()
                elif not custom_field.strip() and not custom_value.strip():
                    st.warning(
                        "⚠️ Please enter both field name and value before adding the filter."
                    )
                elif not custom_field.strip():
                    st.warning("⚠️ Please enter a field name before adding the filter.")
                else:
                    st.warning("⚠️ Please enter a field value before adding the filter.")

    # Return the current filters from session state
    return dict(st.session_state.metadata_filters)


def main() -> None:
    render_svg(svg)
    st.title(app_settings.page_title)

    # Only render metadata filters if using DataRobot RAG (not DIY RAG)
    metadata_filters = None
    if RAG_TYPE == RAGType.DR.value:
        metadata_filters = render_metadata_filters()

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
            with span(
                "rag_completion",
                question_length=len(prompt),
                history_length=len(st.session_state.messages),
                has_metadata_filter=bool(metadata_filters),
            ):
                # Pass metadata filters to the RAG completion (only for DR RAG)
                response = predict.get_rag_completion(
                    question=prompt,
                    messages=st.session_state.messages,
                    metadata_filter=metadata_filters if metadata_filters else None,
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

    if st.session_state.prompt_sent and st.session_state.response:
        render_answer_and_citations(
            answer_and_citations_placeholder,
            st.session_state.response,
        )


if __name__ == "__main__":
    main()
