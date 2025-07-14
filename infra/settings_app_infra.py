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
from datarobot_pulumi_utils.schema.apps import ApplicationSourceArgs
from datarobot_pulumi_utils.schema.exec_envs import RuntimeEnvironments

from docsassist.i18n import LanguageCode, LocaleSettings
from infra.settings_main import PROJECT_ROOT, project_name

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
    base_environment_id=RuntimeEnvironments.PYTHON_312_APPLICATION_BASE.value.id,
    files=source_files,
).model_dump(mode="json", exclude_none=True)

app_resource_name: str = f"Guarded RAG Application [{project_name}]"
