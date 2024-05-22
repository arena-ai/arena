# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Visualize activity
<!-- TODO -->
- Visualize scores
- Added FT capability
- Added small RAG function
- Added a disclaimer about the API tokens uploaded (they should be short term)
- Added the possibility to push some ground truth response

### Fixed



## [0.2.0] - 2024-05-17

### Added

- Name users in the interface
- Display Config in the UI
- Open subscriptions can be done with a GET request

### Fixed

- Fixed worker access to redis (after a failure the worker does not restart)
- Fixed PII substitution
- Fixed delete cascading as https://github.com/tiangolo/sqlmodel/issues/213#issuecomment-1013425005

## [0.1.51] - 2024-05-14

### Added

- Added masking using presidio
- Added masking plus faker
- Added logging before and after masking
- Added masking from any wrapper
- Add a "config" endpoint for masking and evaluation
- Added instrumental evaluation
- Improved the frontend
  - Underline the parent request
  - Wrap lines for the message representation
- Added open user registration
- Fixed the logo in dark mode

## [0.1.38] - 2024-05-02

### Added

- Added a changelog.

### Fixed

- Slow requests.

### Changed

- Changed frontend vs proxy.

### Removed

- Removed PII removal for now.