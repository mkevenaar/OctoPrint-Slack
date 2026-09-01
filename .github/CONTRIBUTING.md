# Contributing to OctoPrint-Slack

Thank you for helping improve OctoPrint-Slack. Bug reports, documentation fixes,
tests, and code changes are welcome.

## Before you start

- Search the existing issues before opening a new one.
- Use the issue forms and include the requested OctoPrint, plugin, and Python
  versions.
- Discuss substantial behavior changes in an issue before investing in an
  implementation.
- Report security vulnerabilities privately as described in
  [SECURITY.md](SECURITY.md).
- Never include a Slack webhook URL, API key, or other secret in an issue, log,
  screenshot, commit, or pull request.

## Development setup

Create and activate a virtual environment, then install an OctoPrint version and
the plugin's test dependencies:

```shell
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install "OctoPrint==2.0.0rc4"
python -m pip install -e ".[test]"
```

Run the test suite:

```shell
python -m pytest
```

To validate the distributable packages:

```shell
python -m pip install build twine
python -m build
python -m twine check dist/*
```

## Making changes

1. Fork the repository and create a focused branch from `develop`.
2. Follow the existing Python and template conventions.
3. Add or update tests for behavior changes.
4. Update documentation when configuration, compatibility, or privacy behavior
   changes.
5. Run the tests and `git diff --check` before submitting your work.

Keep commits focused and write an imperative summary, for example:
`Handle printer storage event origins`.

## Pull requests

Open pull requests against `develop`. Explain the problem and solution, link any
related issue, and list the verification you performed. The CI workflow must
pass before a change is merged.

By participating in this project, you agree to follow the
[Code of Conduct](CODE_OF_CONDUCT.md).
