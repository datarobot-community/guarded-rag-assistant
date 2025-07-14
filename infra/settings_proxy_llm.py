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

import os

import datarobot as dr
import pulumi
import pulumi_datarobot as datarobot
from datarobot_pulumi_utils.schema.custom_models import (
    CustomModelArgs,
    DeploymentArgs,
    RegisteredModelArgs,
)

from docsassist.schema import TARGET_COLUMN_NAME

from .settings_main import (
    default_prediction_server_id,
    project_name,
    runtime_environment_moderations,
)

CHAT_MODEL_NAME = os.getenv("CHAT_MODEL_NAME")

custom_model_args = CustomModelArgs(
    name=f"Guarded RAG Proxy LLM Custom Model [{project_name}]",
    resource_name=f"Guarded RAG Proxy LLM Custom Model [{project_name}]",
    base_environment_id=runtime_environment_moderations.id,
    target_name=TARGET_COLUMN_NAME,
    target_type=dr.enums.TARGET_TYPE.TEXT_GENERATION,
    opts=pulumi.ResourceOptions(delete_before_replace=True),
)

registered_model_args = RegisteredModelArgs(
    resource_name=f"Guarded RAG Proxy LLM Registered Model [{project_name}]",
)


deployment_args = DeploymentArgs(
    resource_name=f"Guarded RAG Proxy LLM Deployment [{project_name}]",
    label=f"Guarded RAG Proxy LLM Deployment [{project_name}]",
    association_id_settings=datarobot.DeploymentAssociationIdSettingsArgs(
        column_names=["association_id"],
        auto_generate_id=False,
        required_in_prediction_requests=True,
    ),
    predictions_settings=(
        None
        if default_prediction_server_id
        else datarobot.DeploymentPredictionsSettingsArgs(min_computes=0, max_computes=1)
    ),
)
