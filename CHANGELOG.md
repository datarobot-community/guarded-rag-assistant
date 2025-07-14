# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased


## [0.2.0] - 2025-07-11

### Added
- Shellcheck configuration for shell script quality assurance
- Chat API enabled by default for enhanced user experience

### Fixed
- Fix prompt column issue by upgrading pulumi-datarobot to 0.10.8

## [0.1.21] - 2025-04-09

### Fixed

- Corrected LLM Proxy settings types in order to fix AttributeError

## [0.1.20] - 2025-04-08

### Added
- Resource bundle config option for the custom model
- Add support for NIM models and existing LLM deployments
- Add chat endpoint to custom deployment

### Changed

- Installed [the datarobot-pulumi-utils library](https://github.com/datarobot-oss/datarobot-pulumi-utils) to incorporate majority of reused logic in the `infra.*` subpackages.

## [0.1.19] - 2025-03-06

### Changed
- Bumped pulumi-datarobot version

### Fixed
- "Usecase already registered" error
- Support is_separator_regex for vector databases

### Added
- Support for existing textgen deployments or registered models
- Add token count and rouge guardrails
- Add feedback mechanism for the DR Q&A App 

## [0.1.18] - 2025-01-18

### Added
- GPT-4o-Mini now an option in the configuration.

### Changed
- Updated system prompt to be more helpful

### Fixed
- Remove environment ID from LLM custom model

## [0.1.17] - 2025-01-15

### Fixed
- Codespace python env no longer broken by quickstart

### Changed
- Move pulumi entrypoint to the infra directory

## [0.1.16] - 2025-01-06

### Added
- RAG deployment now added to the Use Case
- Add customization instructions to the README about system prompts
- Update safe_dump to support unicode

 
### Changed
- More detailed .env.template
- Change of LLM single code change
- More prominent LLM setting
- pulumi-datarobot bumped to 0.5.3
- renamed settings_rag to settings_generative
- Instructions to change the LLM in Readme adjusted to the new process
- Added python 3.9+ requirement to README
- quickstart now asks you to change the default project name
- quickstart now prints the application URL
- Better exception handling around credential validation

### Fixed
- quickstart.py now supports multiline values correctly
- Custom model test works correctly again 

### Added
- Support for AWS Credential type and AWS-based LLM blueprints
- Full testing of the LLM credentials before start

## [0.1.15] - 2024-12-04

### Changed
- update pulumi-datarobot to >=0.4.5
- add pyproject.toml to store lint and test configuration
- update programming language markdown in README
- Give overview of assets in README 
- Move type declarations out of infra.settings_main into docsassist.schema

### Added
- add context tracing to this recipe.

### Removed
- Grader deployment previously included for leveraging predictive models but never fully implemented

## [0.1.14] - 2024-11-18
- ring release/10.2 in sync with main

## [0.1.13] - 2024-11-18

### Changed
- improvements to the README

### Fixed
- Address trailing comments in quickstart
- Added feature flag requirement
  
## [0.1.12] - 2024-11-12

### Changed
- Bring release/10.2 in sync with main

## [0.1.11] - 2024-11-12

### Fixed
- Fix typo in the README for notebooks path
  
### Changed
- Removed locales for unsupported languages
- Updated logos in application

## [0.1.10] - 2024-11-07

### Changed
- Bring release/10.2 in sync with main

## [0.1.9] - 2024-11-07

### Changed
- Fix README typo

## [0.1.8] - 2024-11-06

### Changed
- Bring release/10.2 in sync with main

## [0.1.7] - 2024-11-06

### Added
- quickstart.py script for getting started more quickly

### Removed
- ENABLE_LLM_ASSESSMENT feature flag requirement

## [0.1.6] - 2024-10-30

### Changed
- Bring release/10.2 in sync with main
  
## [0.1.5] - 2024-10-30

### Removed

- ENABLE_QA_APP_TEMPLATE_FROM_REGISTRY feature flag requirement

### Changed

- Default App template set to Streamlit DIY
- Update Running Environment from PYTHON_39_GENAI to PYTHON_311_GENAI in grader

## [0.1.4] - 2024-10-28

### Removed

- datarobot_drum dependency to enable clean statusing from Pulumi CLI on first run (DIY mode)

### Added

- Changelog file to keep track of changes in the project.
