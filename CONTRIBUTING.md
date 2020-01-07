# Development - Contributing

# Requirements
* [poetry](https://github.com/python-poetry/poetry): For dependency management and packaging in Python
* [pre-commit](https://github.com/pre-commit/pre-commit): For identifying code issues before submission to code review

## Developing

To start working on this project, here are some guidelines to set up your environment:
  1. `git clone https://github.com/anancarv/python-artifactory.git`
  2. `cd python-artifactory`
  3. Install poetry: `pip install poetry==0.12.16`
  4. Activate virtualenv`poetry shell`
  5. Install dependencies: `poetry install`
  6. Run `pre-commit install --install-hooks` to install [precommit hooks][pre-commit]

After having installed pre-commit, before each commit, pre-commit hooks are run to:
* check code formatting
* detect secrets
* create TOC in README
* check code typing
* find common security issues in Python code


## Tests

Tests are run with [Pytest](https://docs.pytest.org/en/latest/).
```bash
pytest --cov=pyartifactory --cov-branch --cov-report=xml
```

This command generates a coverage XML file `.coverage.xml`. 

Please, make sure to write tests for each feature you want to implement.
