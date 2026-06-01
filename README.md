# Guarded RAG Assistant
<p align="center">
  <a href="https://app.datarobot.com/usecases/application-templates/66df7eab3168a83282cf4ad7?referrerUrl=github">
    <img src="https://img.shields.io/badge/US-Open%20in%20a%20Codespace-%23909BF5?style=flat&labelColor=%2330373D" alt="US - Open in a Codespace">
  </a>
  <a href="https://app.eu.datarobot.com/usecases/application-templates/66df7eab3168a83282cf4ad7?referrerUrl=github">
    <img src="https://img.shields.io/badge/EU-Open%20in%20a%20Codespace-%232BC46F?labelColor=%2330373D" alt="EU - Open in a Codespace">
  </a>
  <a href="https://app.jp.datarobot.com/usecases/application-templates/66df7eab3168a83282cf4ad7?referrerUrl=github">
    <img src="https://img.shields.io/badge/JP-Open%20in%20a%20Codespace-%23EDA769?labelColor=%2330373D" alt="JP - Open in a Codespace">
  </a>
  <a href="https://app.jp.datarobot.com/usecases/application-templates/66df7eab3168a83282cf4ad7?referrerUrl=github">
    <img src="https://img.shields.io/badge/JP-%E3%80%8CCodespace%20%E3%81%A7%E9%96%8B%E3%81%8F%E3%80%8D-%23EDA769?labelColor=%2330373D" alt="JP - 「Codespaceで開く」">
  </a>
  <a href="https://join.slack.com/t/datarobot-community/shared_invite/zt-3uzfp8k50-SUdMqeux25ok9_5wr4okrg">
    <img src="https://img.shields.io/badge/%23applications-a?label=Slack&labelColor=30373D&color=81FBA6" alt="Slack #applications">
  </a>
</p>

The guarded RAG assistant is an easily customizable recipe for building a RAG-powered chatbot.

In addition to creating a hosted, shareable user interface, the guarded RAG assistant provides:

- Business logic and LLM-based guardrails.
- A predictive secondary model that evaluates response quality.
- GenAI-focused [custom metrics][custom-metrics].
- DataRobot MLOps hosting, monitoring, and governing the individual back-end deployments.

> [!WARNING]
> Application templates are intended to be starting points that provide guidance on how to develop, serve, and maintain AI applications.
> They require a developer or data scientist to adapt and modify them for their business requirements before being put into production.

![Using the Guarded RAG Assistant](https://s3.amazonaws.com/datarobot_public/drx/recipe_gifs/launch_gifs/guardedraghq-small.gif)

[custom-metrics]: https://docs.datarobot.com/en/docs/workbench/nxt-console/nxt-monitoring/nxt-custom-metrics.html

## Table of contents

1. [Quick start](#quick-start)
2. [Architecture overview](#architecture-overview)
3. [Why build AI Apps with DataRobot app templates?](#why-build-ai-apps-with-datarobot-app-templates)
4. [Make changes](#make-changes)
   - [Change the RAG documents](#change-the-rag-documents)
   - [Change the LLM](#change-the-llm)
   - [Add a new LLM](#add-a-new-llm)
   - [Change the RAG prompt](#change-the-RAG-prompt)
   - [Custom front-end](#fully-custom-front-end)
   - [Custom RAG logic](#fully-custom-rag-chunking-vectorization-and-retrieval)
5. [Share results](#share-results)
6. [Delete all provisioned resources](#delete-all-provisioned-resources)
7. [Setup for advanced users](#setup-for-advanced-users)
8. [Data Privacy](#data-privacy)

## 🚀 Quick start

This section outlines how to get started with the Guarded RAG Assistant application template.

### Setup

Use the following resources to locate the required credentials:

- **DataRobot API Token**: Refer to the _Create a DataRobot API Key_ section of the [DataRobot API Quickstart docs](https://docs.datarobot.com/en/docs/api/api-quickstart/index.html#create-a-datarobot-api-key).
- **DataRobot Endpoint**: Refer to the _Retrieve the API Endpoint_ section of the same [DataRobot API Quickstart docs](https://docs.datarobot.com/en/docs/api/api-quickstart/index.html#retrieve-the-api-endpoint).
- **LLM Endpoint and API Key**: Refer to the [Azure OpenAI documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/chatgpt-quickstart?tabs=command-line%2Cjavascript-keyless%2Ctypescript-keyless%2Cpython-new&pivots=programming-language-python#retrieve-key-and-endpoint).

### Build in a DataRobot codespace

If you’re using a DataRobot codespace, everything you need is already installed. You can get the entire application running in just a few minutes using the `dr` CLI.

The fastest way to get started is to run:

```sh
dr start
```

This command will automatically:

- Update the DataRobot CLI (`dr self update`).
- Prepare the environment file if needed (`dr dotenv setup --if-needed`).
- Deploy application (`python quickstart.py`).

  **What does `quickstart.py` do?**

  The quickstart script automates the entire setup process for you:

  - Creates and activates a Python virtual environment
  - Installs all required dependencies via `uv`
  - Loads your `.env` configuration
  - Sets up the Pulumi stack with your project name
  - Runs `pulumi up` to deploy your application
  - Displays your application URL when complete

  This single command replaces all the manual steps described in the [advanced setup section](#setup-for-advanced-users).

  Python 3.10+ is required.

When deployment completes, the terminal will display a link to your running application.\
👉 **Click the link to open and start using your app!**

Advanced users desiring control over virtual environment creation, dependency installation, environment variable setup and `pulumi` invocation see [here](#setup-for-advanced-users).

### Build on your local machine

Follow the steps below to set up your local development environment.

#### Install the DataRobot CLI

> [!NOTE]
> If DataRobot CLI is already installed, you can skip this section.

Follow the installation instructions at: https://github.com/datarobot-oss/cli?tab=readme-ov-file#installation

#### Install Pulumi

> [!NOTE]
> If Pulumi is already installed, you can skip this section.

Follow the installation instructions in the Pulumi [documentation](https://www.pulumi.com/docs/iac/download-install/).
After installing for the first time, **restart your terminal** and run:

```sh
pulumi login --local      # omit --local to use Pulumi Cloud (requires an account)
```

#### Install uv

> [!NOTE]
> If uv is already installed, you can skip this section.

This project uses [uv](https://docs.astral.sh/uv/) for dependency management. Follow the installation instructions at: https://docs.astral.sh/uv/getting-started/installation/

#### Clone the repository

Run the following commands to clone the repository and navigate to the project directory:

```bash
git clone https://github.com/datarobot-community/guarded-rag-assistant.git
cd guarded-rag-assistant
```

#### Quick start

The easiest way to set up and start developing locally is to run:

```sh
dr start
```

When deployment completes, the terminal will display a link to your running application.\
👉 **Click the link to open and start using your app!**

## Architecture overview

![Guarded RAG architecture](https://s3.amazonaws.com/datarobot_public/drx/recipe_gifs/rag_architecture.svg)

App templates contain three families of complementary logic. For Guarded RAG you can [opt-in](#make-changes) to fully
custom RAG logic and a fully custom frontend or utilize DR's off the shelf offerings:

- **AI logic**: Necessary to service AI requests and produce predictions and completions.
  ```
  deployment_*/  # Predictive model scoring logic, RAG completion logic (DIY RAG)
  notebooks/  # Document chunking, VDB creation logic (DIY RAG)
  ```
- **App Logic**: Necessary for user consumption; whether via a hosted front-end or integrating into an external consumption layer.
  ```
  frontend/  # Streamlit frontend (DIY frontend)
  docsassist/  # App business logic & runtime helpers (DIY front-end)
  ```
- **Operational Logic**: Necessary to activate DataRobot assets.
  ```
  infra/  # Settings for resources and assets to be created in DataRobot
  infra/__main__.py  # Pulumi program for configuring DataRobot to serve and monitor AI and App logic
  ```

## Why build AI Apps with DataRobot app templates?

App Templates transform your AI projects from notebooks to production-ready applications. Too often, getting models into production means rewriting code, juggling credentials, and coordinating with multiple tools & teams just to make simple changes. DataRobot's composable AI apps framework eliminates these bottlenecks, letting you spend more time experimenting with your ML and app logic and less time wrestling with plumbing and deployment.

- Start building in minutes: Deploy complete AI applications instantly, then customize the AI logic or the front-end independently (no architectural rewrites needed).
- Keep working your way: Data scientists keep working in notebooks, developers in IDEs, and configs stay isolated. Update any piece without breaking others.
- Iterate with confidence: Make changes locally and deploy with confidence. Spend less time writing and troubleshooting plumbing and more time improving your app.

Each template provides an end-to-end AI architecture, from raw inputs to deployed application, while remaining highly customizable for specific business requirements.

## Make changes

### Change the RAG documents

1. Replace `assets/datarobot_english_documentation_docsassist.zip` with a new zip file containing .pdf, .docx,
   .md, or .txt documents ([example alternative docs here](https://s3.amazonaws.com/datarobot_public_datasets/ai_accelerators/acme_corp_company_policies_source_business_victoria_templates.zip)).
2. Update the `rag_documents` setting in `infra/settings_main.py` to specify the local path to the
   new zip file.
3. Run `pulumi up` to update your stack.
   ```bash
   source set_env.sh  # On windows use `set_env.bat`
   pulumi up
   ```

### Change the LLM

1. Modify the `LLM` setting in `infra/settings_generative.py` by changing `LLM=LLMs.AZURE_OPENAI_GPT_4_O` to any other LLM from the `LLMs` object.
   - Trial users: Please set `LLM=LLMs.AZURE_OPENAI_GPT_4_O_MINI` since GPT-4o is not supported in the trial. Use the `OPENAI_API_DEPLOYMENT_ID` in `.env` to override which model is used in your Azure organization. You'll still see GPT 4o-mini in the playground, but the deployed app will use the provided Azure deployment.
2. To use an existing TextGen model or deployment:
   - In `infra/settings_generative.py`: Set `LLM=LLMs.DEPLOYED_LLM`.
   - In `.env`: Set either the `TEXTGEN_REGISTERED_MODEL_ID` or the `TEXTGEN_DEPLOYMENT_ID`
   - In `.env`: Set `CHAT_MODEL_NAME` to the model name expected by the deployment (e.g. "claude-3-7-sonnet-20250219" for an anthropic deployment,"datarobot-deployed-llm" for NIM models )
3. In `.env`: If not using an existing TextGen model or deployment, provide the required credentials dependent on your choice.
4. Run `pulumi up` to update your stack (Or rerun your quickstart).
   ```bash
   source set_env.sh  # On windows use `set_env.bat`
   pulumi up
   ```

> **⚠️ Availability information:**  
> Using a NIM model requires custom model GPU inference, a premium feature. You will experience errors by using this type of model without the feature enabled. Contact your DataRobot representative or administrator for information on enabling this feature.

### Add a new LLM

If the LLM you want to use isn't already defined in the `LLMs` object, you can register it manually using `LLMConfig`.

1. Find the ID of the LLM you want to add by running the following in a Python session:

   ```python
   import datarobot
   print('\n'.join([i['id'] for i in datarobot.genai.LLMDefinition.list()]))
   ```

2. In `infra/settings_generative.py`, add `LLMConfig` to the existing import and register the new LLM before the `LLM =` assignment:

   ```python
   from datarobot_pulumi_utils.schema.llms import (
       LLMBlueprintArgs,
       LLMConfig,
       LLMs,
       LLMSettings,
       PlaygroundArgs,
   )

   LLMs.YOUR_LLM_NAME = LLMConfig(name="YOUR_LLM_ID", credential_type="azure")
   LLM = LLMs.YOUR_LLM_NAME
   ```

   Replace `YOUR_LLM_NAME` with a descriptive attribute name and `YOUR_LLM_ID` with the ID from step 1.

3. In `utils/credentials.py`, add a mapping from the new LLM name to its Azure deployment name inside the `get_credentials` function:

   ```python
   LLMs.YOUR_LLM_NAME.name: "YOUR_AZURE_DEPLOYMENT_NAME",
   ```

4. Run `pulumi up` to update your stack.

   ```bash
   source set_env.sh  # On windows use `set_env.bat`
   pulumi up
   ```

### Change the RAG prompt

1. Modify the `system_prompt` variable in `infra/settings_generative.py` with your desired prompt.
2. If using [fully custom RAG logic](#fully-custom-rag-chunking-vectorization-and-retrieval), instead please change the `stuff_prompt` variable in `notebooks/build_rag.ipynb`.

### Fully custom front-end

1. Edit `infra/settings_main.py` and update `application_type` to `ApplicationType.DIY`
   - Optionally, update `APP_LOCALE` in `docsassist/i18n.py` to toggle the language.
     Supported locales are Japanese and English, with English set as the default.
2. Run `pulumi up` to update your stack with the example custom Streamlit frontend:
   ```bash
   source set_env.sh  # On windows use `set_env.bat`
   pulumi up
   ```
3. After provisioning the stack at least once, you can also edit and test the Streamlit
   front-end locally using `streamlit run app.py` from the `frontend/` directory (don't
   forget to initialize your environment using `set_env`).
   ```bash
   source set_env.sh  # On windows use `set_env.bat`
   cd frontend
   streamlit run app.py
   ```

### Fully custom RAG chunking, vectorization, and retrieval

1. Install additional requirements (e.g. FAISS, HuggingFace).
   ```bash
   source set_env.sh  # On windows use `set_env.bat`
   uv sync --extra rag-diy
   ```
2. Edit `infra/settings_main.py` and update `rag_type` to `RAGType.DIY`.
3. Run `pulumi up` to update your stack with the example custom RAG logic.
   ```bash
   source set_env.sh  # On windows use `set_env.bat`
   pulumi up
   ```
4. Edit `notebooks/build_rag.ipynb` to customize the doc chunking, vectorization logic.
5. Edit `deployment_diy_rag/custom.py` to customize the retrieval logic & LLM call.
6. Run `pulumi up` to update your stack.
   ```bash
   source set_env.sh  # On windows use `set_env.bat`
   pulumi up
   ```

## Share results

1. Log into the DataRobot application.
2. Navigate to **Registry > Applications**.
3. Navigate to the application you want to share, open the actions menu, and select **Share** from the dropdown.

## Delete all provisioned resources

```bash
pulumi down
```

## Setup for advanced users

For manual control over the setup process, adapt the following steps for macOS/Linux to your environment:

```bash
uv sync
source .venv/bin/activate
source set_env.sh
pulumi stack init YOUR_PROJECT_NAME
pulumi up
```

`uv sync` creates the virtual environment and installs all pinned dependencies from `uv.lock` automatically. On Windows:

```bash
uv sync
.venv\Scripts\activate
set_env.bat
pulumi stack init YOUR_PROJECT_NAME
pulumi up
```

For projects that will be maintained, DataRobot recommends forking the repo so upstream fixes and improvements can be merged in the future.

## Data Privacy

Your data privacy is important to us. Data handling is governed by the DataRobot [Privacy Policy](https://www.datarobot.com/privacy/), please review before using your own data with DataRobot.
