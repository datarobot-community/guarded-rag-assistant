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
import json
import textwrap

import datarobot as dr
import pulumi_datarobot as datarobot
from datarobot_pulumi_utils.schema.custom_models import (
    CustomModelArgs,
    DeploymentArgs,
    RegisteredModelArgs,
)
from datarobot_pulumi_utils.schema.guardrails import (
    Condition,
    CustomModelGuardConfigurationArgs,
    GuardConditionComparator,
    GuardrailTemplateNames,
    Intervention,
    ModerationAction,
    Stage,
)

from docsassist.i18n import gettext

from .settings_main import (
    PROJECT_ROOT,
    default_prediction_server_id,
    project_name,
    runtime_environment_moderations,
)

keyword_guard_target_name = "flagged"
keyword_guard_positive_class_label = "true"
keyword_guard_negative_class_label = "false"

custom_model_args = CustomModelArgs(
    name=f"Keyword Guard Custom Model [{project_name}]",
    resource_name=f"Keyword Guard Custom Model [{project_name}]",
    description="This model is designed to guard against questions about competitors",
    base_environment_id=runtime_environment_moderations.id,
    target_name=keyword_guard_target_name,
    target_type=dr.enums.TARGET_TYPE.BINARY,
    positive_class_label=keyword_guard_positive_class_label,
    negative_class_label=keyword_guard_negative_class_label,
    runtime_parameter_values=[
        datarobot.CustomModelRuntimeParameterValueArgs(
            key="blocklist",
            type="string",
            value=json.dumps(
                [
                    "dataiku",
                    "databrick",
                    "h20",
                    "microsoft",
                    "gcp",
                    "google",
                    "vertex\\s*ai",
                    "compet",
                ]
            ),
        ),
        datarobot.CustomModelRuntimeParameterValueArgs(
            key="prompt_feature_name",
            type="string",
            value="guardrailText",
        ),
    ],
    folder_path=str(PROJECT_ROOT / "deployment_keyword_guard"),
)

registered_model_args = RegisteredModelArgs(
    resource_name=f"Keyword Guard Registered Model [{project_name}]",
)

deployment_args = DeploymentArgs(
    resource_name=f"Keyword Guard Deployment [{project_name}]",
    label=f"Keyword Guard Deployment [{project_name}]",
    predictions_settings=(
        None
        if default_prediction_server_id
        else datarobot.DeploymentPredictionsSettingsArgs(min_computes=0, max_computes=1)
    ),
)

custom_model_guard_configuration_args = CustomModelGuardConfigurationArgs(
    template_name=GuardrailTemplateNames.CUSTOM_DEPLOYMENT,
    name=f"Keyword Guard Configuration [{project_name}]",
    stages=[Stage.PROMPT],
    intervention=Intervention(
        action=ModerationAction.BLOCK,
        condition=Condition(
            comparand=1,
            comparator=GuardConditionComparator.EQUALS,
        ).model_dump_json(),
        message=textwrap.dedent(
            gettext(
                """\
                I have detected you are asking about another vendor. I hear they have great products, but I think DataRobot is the best.

                For information on integrations, please check our website here:
                https://docs.datarobot.com/en/docs/more-info/how-to/index.html"""
            )
        ),
    ),
    input_column_name="guardrailText",
    output_column_name=f"{keyword_guard_target_name}_{keyword_guard_positive_class_label}_PREDICTION",
)
