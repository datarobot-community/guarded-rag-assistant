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


import datarobot as dr

from docsassist.i18n import LanguageCode, LocaleSettings
from infra.common.globals import GlobalRuntimeEnvironment
from infra.common.schema import ApplicationSourceArgs
from infra.settings_main import PROJECT_ROOT, project_name


def get_app_template_id(name: str) -> str:
    client = dr.client.get_client()
    try:
        templates = client.get(
            "customTemplates/", params={"templateType": "customApplicationTemplate"}
        ).json()
        template_id: str = next(
            template["id"] for template in templates["data"] if template["name"] == name
        )
        return template_id
    except Exception as e:
        raise ValueError(
            f"Could not find the Application Template ID for {name}"
        ) from e


_application_path = PROJECT_ROOT / "frontend"


source_files = [
    (str(f), str(f.relative_to(_application_path)))
    for f in _application_path.glob("**/*")
    if f.is_file()
]

docsassist_path = PROJECT_ROOT / "docsassist"

source_files.extend(
    [
        (str(docsassist_path / "__init__.py"), "docsassist/__init__.py"),
        (str(docsassist_path / "deployments.py"), "docsassist/deployments.py"),
        (str(docsassist_path / "predict.py"), "docsassist/predict.py"),
        (str(docsassist_path / "schema.py"), "docsassist/schema.py"),
        (str(docsassist_path / "i18n.py"), "docsassist/i18n.py"),
    ]
)

application_locale = LocaleSettings().app_locale

if application_locale != LanguageCode.EN:
    source_files.append(
        (
            str(
                docsassist_path
                / "locale"
                / application_locale
                / "LC_MESSAGES"
                / "base.mo"
            ),
            f"docsassist/locale/{application_locale}/LC_MESSAGES/base.mo",
        )
    )

app_source_args = ApplicationSourceArgs(
    resource_name=f"Guarded RAG App Source [{project_name}]",
    base_environment_id=GlobalRuntimeEnvironment.PYTHON_39_STREAMLIT.value.id,
    files=source_files,
).model_dump(mode="json", exclude_none=True)

app_resource_name: str = f"Guarded RAG Application [{project_name}]"
