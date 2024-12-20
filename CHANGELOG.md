# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.15] - 2024-12-04

### Changed
- update pulumi-datarobot to >=0.4.5
- add pyproject.toml to store lint and test configuration
- update programming language markdown in README
- Give overview of assets in README 
- Move type declarations out of infra.settings_main into docsassist.schema

### Added
- add context tracing to this recipe.

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
