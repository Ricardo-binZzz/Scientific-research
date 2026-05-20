# Security Policy

## Supported Versions

This project is early-stage. Security fixes should target the current `main` branch.

## Reporting a Vulnerability

Please do not open public issues for secrets, private data exposure, or code execution vulnerabilities.

Report privately through GitHub's private vulnerability reporting if it is enabled for this repository. If private reporting is not available, contact the repository owner through a non-public channel and include:

- a short description of the issue
- affected files or commands
- steps to reproduce
- expected impact
- whether any private data, credentials, or unpublished research material may be exposed

## Data Handling Expectations

This project is local-first and should not require cloud accounts or remote services for core workflows. Contributors should avoid committing:

- API keys, tokens, passwords, cookies, or session files
- personal Windows/macOS/Linux home-directory paths
- unpublished papers or private PDFs
- private simulation exports or thesis data
- identifiable student, reviewer, or collaborator information

Use generic examples such as `C:\Users\YourName\Documents\fixture-study` in documentation.
