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
import os
import pathlib
import sys

import papermill as pm
import pulumi
import pulumi_datarobot as datarobot
from datarobot_pulumi_utils.common import check_feature_flags
from datarobot_pulumi_utils.common.urls import get_deployment_url
from datarobot_pulumi_utils.pulumi.custom_model_deployment import CustomModelDeployment
from datarobot_pulumi_utils.pulumi.proxy_llm_blueprint import ProxyLLMBlueprint
from datarobot_pulumi_utils.schema.apps import ApplicationTemplates
from datarobot_pulumi_utils.schema.llms import LLMs

sys.path.append("..")

from docsassist.deployments import (
    app_env_name,
    rag_deployment_env_name,
)
from docsassist.i18n import LocaleSettings
from docsassist.schema import ApplicationType, RAGType
from infra import (
    settings_app_infra,
    settings_generative,
    settings_guardrails,
    settings_keyword_guard,
    settings_main,
)
from infra.settings_global_model_guardrails import global_guardrails
from infra.settings_proxy_llm import CHAT_MODEL_NAME
from utils.credentials import get_credential_runtime_parameter_values, get_credentials

TEXTGEN_DEPLOYMENT_ID = os.environ.get("TEXTGEN_DEPLOYMENT_ID")
TEXTGEN_REGISTERED_MODEL_ID = os.environ.get("TEXTGEN_REGISTERED_MODEL_ID")

if settings_generative.LLM == LLMs.DEPLOYED_LLM:
    pulumi.info(f"{TEXTGEN_DEPLOYMENT_ID=}")
    pulumi.info(f"{TEXTGEN_REGISTERED_MODEL_ID=}")
    if (TEXTGEN_DEPLOYMENT_ID is None) == (TEXTGEN_REGISTERED_MODEL_ID is None):  # XOR
        raise ValueError(
            "Either TEXTGEN_DEPLOYMENT_ID or TEXTGEN_REGISTERED_MODEL_ID must be set when using a deployed LLM. Plese check your .env file"
        )

LocaleSettings().setup_locale()

check_feature_flags(pathlib.Path("feature_flag_requirements.yaml"))

if "DATAROBOT_DEFAULT_USE_CASE" in os.environ:
    use_case_id = os.environ["DATAROBOT_DEFAULT_USE_CASE"]
    pulumi.info(f"Using existing use case '{use_case_id}'")
    use_case = datarobot.UseCase.get(
        id=use_case_id,
        resource_name="Guarded RAG Use Case [PRE-EXISTING]",
    )
else:
    use_case = datarobot.UseCase(**settings_main.use_case_args)

if settings_main.default_prediction_server_id is None:
    prediction_environment = datarobot.PredictionEnvironment(
        **settings_main.prediction_environment_args,
    )
else:
    prediction_environment = datarobot.PredictionEnvironment.get(
        "Guarded RAG Prediction Environment [PRE-EXISTING]",
        settings_main.default_prediction_server_id,
    )

credentials = get_credentials(settings_generative.LLM)

credential_runtime_parameter_values = get_credential_runtime_parameter_values(
    credentials=credentials
)

keyword_guard_deployment = CustomModelDeployment(
    resource_name=f"Keyword Guard [{settings_main.project_name}]",
    custom_model_args=settings_keyword_guard.custom_model_args,
    registered_model_args=settings_keyword_guard.registered_model_args,
    prediction_environment=prediction_environment,
    deployment_args=settings_keyword_guard.deployment_args,
)

global_guard_deployments = [
    datarobot.Deployment(
        registered_model_version_id=datarobot.get_global_model(
            name=guard.registered_model_name,
        ).version_id,
        prediction_environment_id=prediction_environment.id,
        use_case_ids=[use_case.id],
        **guard.deployment_args.model_dump(),
    )
    for guard in global_guardrails
]

all_guard_deployments = [keyword_guard_deployment] + global_guard_deployments

all_guardrails_configs = [
    settings_keyword_guard.custom_model_guard_configuration_args
] + [guard.custom_model_guard_configuration_args for guard in global_guardrails]


guard_configurations = [
    datarobot.CustomModelGuardConfigurationArgs(
        deployment_id=deployment.id,
        **guard_config_args.model_dump(mode="json", exclude_none=True),
    )
    for deployment, guard_config_args in zip(
        all_guard_deployments,
        all_guardrails_configs,
    )
] + settings_guardrails.guardrails

if settings_main.core.rag_type == RAGType.DR:
    dataset = datarobot.DatasetFromFile(
        use_case_ids=[use_case.id],
        **settings_generative.dataset_args.model_dump(),
    )
    vector_database = datarobot.VectorDatabase(
        dataset_id=dataset.id,
        use_case_id=use_case.id,
        **settings_generative.vector_database_args.model_dump(),
    )
    playground = datarobot.Playground(
        use_case_id=use_case.id,
        **settings_generative.playground_args.model_dump(),
    )

    if settings_generative.LLM == LLMs.DEPLOYED_LLM:
        if TEXTGEN_REGISTERED_MODEL_ID is not None:
            proxy_llm_registered_model = datarobot.RegisteredModel.get(
                resource_name="Existing TextGen Registered Model",
                id=TEXTGEN_REGISTERED_MODEL_ID,
            )

            proxy_llm_deployment = datarobot.Deployment(
                resource_name=f"Guarded RAG LLM Deployment [{settings_main.project_name}]",
                registered_model_version_id=proxy_llm_registered_model.version_id,
                prediction_environment_id=prediction_environment.id,
                label=f"Guarded RAG Assistant LLM Deployment [{settings_main.project_name}]",
                use_case_ids=[use_case.id],
                opts=pulumi.ResourceOptions(
                    replace_on_changes=["registered_model_version_id"]
                ),
            )
        elif TEXTGEN_DEPLOYMENT_ID is not None:
            proxy_llm_deployment = datarobot.Deployment.get(
                resource_name="Existing LLM Deployment", id=TEXTGEN_DEPLOYMENT_ID
            )
        else:
            raise ValueError(
                "Either TEXTGEN_REGISTERED_MODEL_ID or TEXTGEN_DEPLOYMENT_ID have to be set in `.env`"
            )

        llm_blueprint = ProxyLLMBlueprint(
            use_case_id=use_case.id,
            playground_id=playground.id,
            proxy_llm_deployment_id=proxy_llm_deployment.id,
            vector_database_id=vector_database.id,
            chat_model_name=CHAT_MODEL_NAME,
            **settings_generative.llm_blueprint_args.model_dump(mode="python"),
        )

    elif settings_generative.LLM != LLMs.DEPLOYED_LLM:
        llm_blueprint = datarobot.LlmBlueprint(  # type: ignore[assignment]
            playground_id=playground.id,
            vector_database_id=vector_database.id,
            **settings_generative.llm_blueprint_args.model_dump(),
        )

    rag_custom_model = datarobot.CustomModel(
        **settings_generative.custom_model_args.model_dump(exclude_none=True),
        use_case_ids=[use_case.id],
        source_llm_blueprint_id=llm_blueprint.id,
        guard_configurations=guard_configurations,
        runtime_parameter_values=[]
        if settings_generative.LLM == LLMs.DEPLOYED_LLM
        else credential_runtime_parameter_values,
    )

elif settings_main.core.rag_type == RAGType.DIY:
    if not all(
        [
            path.exists()
            for path in settings_generative.diy_rag_nb_output.model_dump().values()
        ]
    ):
        pulumi.info("Executing doc chunking + vdb building notebook...")
        pm.execute_notebook(
            settings_generative.diy_rag_nb,
            output_path=None,
            cwd=settings_generative.diy_rag_nb.parent,
            log_output=False,
            progress_bar=False,
            stderr_file=sys.stderr,
            stdout_file=sys.stdout,
        )
    else:
        pulumi.info(
            f"Using existing outputs from build_rag.ipynb in '{settings_generative.diy_rag_deployment_path}'"
        )

    rag_custom_model = datarobot.CustomModel(
        files=settings_generative.get_diy_rag_files(
            runtime_parameter_values=credential_runtime_parameter_values,
        ),
        runtime_parameter_values=credential_runtime_parameter_values,
        guard_configurations=guard_configurations,
        use_case_ids=[use_case.id],
        **settings_generative.custom_model_args.model_dump(
            mode="json", exclude_none=True
        ),
    )
else:
    raise NotImplementedError(f"Unknown RAG type: {settings_main.core.rag_type}")

rag_deployment = CustomModelDeployment(
    resource_name=f"Guarded RAG Deploy [{settings_main.project_name}]",
    custom_model_version_id=rag_custom_model.version_id,
    registered_model_args=settings_generative.registered_model_args,
    prediction_environment=prediction_environment,
    deployment_args=settings_generative.deployment_args,
    use_case_ids=[use_case.id],
)

app_runtime_parameters = [
    datarobot.ApplicationSourceRuntimeParameterValueArgs(
        key=rag_deployment_env_name, type="deployment", value=rag_deployment.id
    ),
    datarobot.ApplicationSourceRuntimeParameterValueArgs(
        key="APP_LOCALE", type="string", value=LocaleSettings().app_locale
    ),
]

if settings_main.core.application_type == ApplicationType.DIY:
    application_source = datarobot.ApplicationSource(
        runtime_parameter_values=app_runtime_parameters,
        **settings_app_infra.app_source_args,
    )
    qa_application = datarobot.CustomApplication(
        resource_name=settings_app_infra.app_resource_name,
        source_version_id=application_source.version_id,
        use_case_ids=[use_case.id],
    )
elif settings_main.core.application_type == ApplicationType.DR:
    feedback_metric = datarobot.CustomMetric(
        resource_name="Feedback Metric",
        deployment_id=rag_deployment.id,
        baseline_value=0.5,
        directionality="higherIsBetter",
        units="Positive Feedback",
        type="average",
        is_model_specific=True,
        is_geospatial=False,
    )

    app_source = datarobot.ApplicationSourceFromTemplate(
        resource_name=f"Guarded RAG Assistant App Source [{settings_main.project_name}]",
        template_id=ApplicationTemplates.Q_AND_A_CHAT_GENERATION_APP.value.id,
        runtime_parameter_values=[
            datarobot.ApplicationSourceFromTemplateRuntimeParameterValueArgs(
                key="DEPLOYMENT_ID", value=rag_deployment.id, type="deployment"
            ),
            datarobot.ApplicationSourceFromTemplateRuntimeParameterValueArgs(
                key="CUSTOM_METRIC_ID", value=feedback_metric.id, type="string"
            ),
            datarobot.ApplicationSourceFromTemplateRuntimeParameterValueArgs(
                key="ENABLE_CHAT_API", value="True", type="boolean"
            ),
        ],
    )
    qa_application = datarobot.CustomApplication(
        resource_name=settings_app_infra.app_resource_name,
        name=f"Guarded RAG Assistant [{settings_main.project_name}]",
        source_version_id=app_source.version_id,
        allow_auto_stopping=True,
        use_case_ids=[use_case.id],
        opts=pulumi.ResourceOptions(
            delete_before_replace=True, depends_on=[app_source]
        ),
        resources=app_source.resources,
    )
else:
    raise NotImplementedError(
        f"Unknown application type: {settings_main.core.application_type}"
    )


pulumi.export(rag_deployment_env_name, rag_deployment.id)
pulumi.export(app_env_name, qa_application.id)
for deployment, config in zip(global_guard_deployments, global_guardrails):
    pulumi.export(
        config.deployment_args.resource_name,
        deployment.id.apply(get_deployment_url),
    )

pulumi.export(
    settings_generative.deployment_args.resource_name,
    rag_deployment.id.apply(get_deployment_url),
)
pulumi.export(
    settings_app_infra.app_resource_name,
    qa_application.application_url,
)
