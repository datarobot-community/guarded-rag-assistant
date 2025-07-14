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
import re

import pandas as pd
from datarobot_drum import RuntimeParameters


def load_model(code_dir):
    blocklist = json.loads(RuntimeParameters.get("blocklist"))
    prompt_feature_name = RuntimeParameters.get("prompt_feature_name")
    regex = "({})".format("|".join([keyword for keyword in blocklist]))
    return regex, prompt_feature_name


def score(data, model, **kwargs):
    regex, prompt_feature_name = model

    output = []
    positive_label = kwargs["positive_class_label"]
    negative_label = kwargs["negative_class_label"]
    for prompt in data[prompt_feature_name]:
        block_input = bool(re.search(regex, prompt, re.IGNORECASE))
        output.append(
            {positive_label: float(block_input), negative_label: 1 - float(block_input)}
        )
    return pd.DataFrame(output)
