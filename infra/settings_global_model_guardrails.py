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
import pulumi_datarobot as datarobot
from datarobot_pulumi_utils.schema.custom_models import DeploymentArgs
from datarobot_pulumi_utils.schema.guardrails import (
    Condition,
    CustomModelGuardConfigurationArgs,
    GuardConditionComparator,
    GuardrailModelNames,
    GuardrailTemplateNames,
    Intervention,
    ModerationAction,
    Stage,
)
from pydantic import BaseModel

from docsassist.i18n import gettext

from .settings_main import default_prediction_server_id, project_name


class GlobalGuardrail(BaseModel):
    deployment_args: DeploymentArgs
    registered_model_name: GuardrailModelNames
    custom_model_guard_configuration_args: CustomModelGuardConfigurationArgs


toxicity = GlobalGuardrail(
    deployment_args=DeploymentArgs(
        resource_name=f"Toxicity Guard Deployment [{project_name}]",
        label=f"Toxicity Guard [{project_name}]",
        predictions_settings=(
            None
            if default_prediction_server_id
            else datarobot.DeploymentPredictionsSettingsArgs(
                min_computes=0, max_computes=1
            )
        ),
    ),
    registered_model_name=GuardrailModelNames.TOXICITY,
    custom_model_guard_configuration_args=CustomModelGuardConfigurationArgs(
        name=f"Toxicity Guard Configuration [{project_name}]",
        template_name=GuardrailTemplateNames.TOXICITY,
        stages=[Stage.PROMPT],
        intervention=Intervention(
            action=ModerationAction.BLOCK,
            condition=Condition(
                comparand=0.7,
                comparator=GuardConditionComparator.GREATER_THAN,
            ).model_dump_json(),
            message=gettext(
                "I have detected that your question contains toxic language. Please rephrase your question."
            ),
        ),
    ),
)

prompt_injection = GlobalGuardrail(
    deployment_args=DeploymentArgs(
        resource_name=f"Prompt Injection Guard Deployment [{project_name}]",
        label=f"Prompt Injection Guard [{project_name}]",
        predictions_settings=(
            None
            if default_prediction_server_id
            else datarobot.DeploymentPredictionsSettingsArgs(
                min_computes=0, max_computes=1
            )
        ),
    ),
    registered_model_name=GuardrailModelNames.PROMPT_INJECTION,
    custom_model_guard_configuration_args=CustomModelGuardConfigurationArgs(
        name=f"Prompt Injection Guard Configuration [{project_name}]",
        template_name=GuardrailTemplateNames.PROMPT_INJECTION,
        stages=[Stage.PROMPT],
        intervention=Intervention(
            action=ModerationAction.BLOCK,
            condition=Condition(
                comparand=0.7,
                comparator=GuardConditionComparator.GREATER_THAN,
            ).model_dump_json(),
            message=gettext(
                "I have detected that your question contains a prompt injection. Please rephrase your question."
            ),
        ),
    ),
)


global_guardrails = [toxicity, prompt_injection]
