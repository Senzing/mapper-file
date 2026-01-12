# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

mapper-file is a Senzing Python utility for file mapping operations. It's part of the Senzing ecosystem for entity resolution.

## Development Commands

### Environment Setup

```bash
python -m venv ./venv
source ./venv/bin/activate
python -m pip install --upgrade pip
python -m pip install --group all .
```

### Linting

```bash
# Run pylint on all Python files (excludes docs/source)
pylint $(git ls-files '*.py' ':!:docs/source/*')

# Format with black
black .

# Sort imports
isort .

# Security check
bandit -r src/

# Type checking
mypy src/
```

## Code Style

- Line length: 120 characters
- Use black for formatting with isort profile
- Python 3.10+ required
- Follow pylint rules defined in pyproject.toml (some rules disabled: `consider-using-with`, `invalid-name`, `line-too-long`, `too-many-branches`, `too-many-lines`, `too-many-statements`, `unspecified-encoding`)

## Project Structure

- `src/` - Main source code
- `docs/` - Documentation (GitHub Pages placeholder)
- `.github/workflows/` - CI pipelines (pylint, spellcheck)

## CI Checks

Pull requests trigger:
- Pylint across Python 3.10, 3.11, 3.12, 3.13
- Spellcheck via cspell

## Commit Guidelines

Do not include "Co-authored-by" lines in commits (configured in `.claude/settings.json`).
