# Copyright 2026 DataRobot, Inc.
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

import logging
import os
from contextlib import contextmanager
from typing import Generator

logger = logging.getLogger(__name__)

_tracer = None
_initialized = False


def _is_enabled() -> bool:
    if os.getenv("DISABLE_TELEMETRY", "").lower() in ("1", "true", "yes"):
        return False
    return bool(os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"))


def init_telemetry(service_name: str = "docsassist") -> None:
    """Initialize OpenTelemetry. No-op if OTEL_EXPORTER_OTLP_ENDPOINT is unset or
    DISABLE_TELEMETRY is set."""
    global _tracer, _initialized
    if _initialized:
        return
    _initialized = True

    if not _is_enabled():
        logger.debug("Telemetry disabled — set OTEL_EXPORTER_OTLP_ENDPOINT to enable")
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
        trace.set_tracer_provider(provider)

        # Auto-instrument httpx — captures all outbound HTTP calls including the
        # OpenAI client requests to the DataRobot deployment
        HTTPXClientInstrumentor().instrument()

        _tracer = trace.get_tracer(service_name)
        logger.info(
            "Telemetry initialized (OTLP → %s)",
            os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
        )
    except Exception:
        logger.exception("Failed to initialize telemetry — continuing without it")


@contextmanager
def span(name: str, **attrs: str | int | float | bool) -> Generator[None, None, None]:
    """Create a trace span if telemetry is active, otherwise no-op."""
    if _tracer is None:
        yield
        return

    from opentelemetry import trace

    with _tracer.start_as_current_span(name) as s:
        for k, v in attrs.items():
            s.set_attribute(k, v)
        try:
            yield
        except Exception as exc:
            s.set_status(trace.StatusCode.ERROR, str(exc))
            s.record_exception(exc)
            raise
