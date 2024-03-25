# Python Reference Architecture 

The main objective of this repository is to lay out the tools and packages that are mainly used for app development in python.

## Contents

- [Project Structure](#project-structure)
- [Local Environment Setup](#local-environment-setup)
- [CDK Setup](#cdk-setup)
- [Pre Commit Setup](#pre-commit-setup)
- [Packages and Tools](#packages-and-tools)

## Project Structure

The project is divided into two main application python packages: `src` and `infrastructure`.

### Src Package

This package holds the python code for the application we want to develop. This includes the core application code, the main output ports (http servers, stream consumers, lambda functions, etc), tests packages and general configuration.
The top level directory is shown below:

```commandline
src
├── app
│   ├── ...
├── config.py
├── http
│   ├── ...
├── lambda_functions
│   ├── ...
├── test
│   ├── ...

```

- `app`: holds the main application code based on Hexagonal Architecture design pattern.
- `http`: http server implementation.
- `lambda_functions`: implementation of AWS lambda functions.
- `test`: holds the different types of tests to be executed in CI/CD.
- `config.py`: general configuration file

### Infrastructure Package

This package contains our CDK python app and general configuration. This will follow the basic structure recommended by AWS.
The top level directory is shown below:

```commandline
infrastructure
├── app.py
└── stacks
    ├── __init__.py
    ├── config.py
    └── ...
```

- `app.py`: the main CDK app used for deployment of resource stacks to AWS.
- `stacks`: the package where our CDK Stacks classes will be defined.
- `stacks/config.py`: general configuration for CDK app.

## Local Environment Setup

### Setting up Poetry:

*Python 3.12 is required*

The virtual environment is generated with [poetry](https://python-poetry.org).

To install poetry you can follow the method of your choice described [here](https://python-poetry.org/docs/#installing-with-pipx)

In the project's root execute to instantiate poetry's shell and create the virtual environment defined in the `pyproject.toml`:

```shell script
poetry shell 
```

Make sure you have python 3.12 or higher installed in your system.

Install all the packages specified in the `pyproject.toml`:

```shell script
poetry install
```

When updating dependencies, execute the update command:

```shell script
poetry update
```

### Executing development tasks

Using the `Invoke` commands, you can control the development tasks. 

Run static type checking with mypy:

```shell script
poetry run invoke mypy
```

To run the tests with coverage check:

```shell script
poetry run invoke tests
```

This command will generate the html coverage report and store it htmlcov folder in the project's root directory.

To run `Black` code formatter:

```shell script
poetry run invoke formatcode
```

To run all the tasks above:

```shell script
poetry run invoke validate
```

To run the http server:

```shell script
poetry run invoke runhttp
```

## CDK Setup

We will be using [AWS CDK](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html) for Infrastructure as Code.

### Installing CDK

To install CDK you will need to download `npm` and then execute:

```shell script
npm i -g aws-cdk
```

### Environment Variables

For local testing and deployment to an `aws development environment` it is required to export the following environment variables:

```
export AWS_ACCOUNT_ID={AWS DEVELOPMENT ACCOUNT ID}
export AWS_REGION={DEFAULT TESTING REGION}
export AWS_ACCESS_KEY_ID={TEMPORARY ACCESS KEY PROVIDED BY AWS SSO}
export AWS_SECRET_ACCESS_KEY={TEMPORARY SECRET KEY PROVIDED BY AWS SSO}
export AWS_SESSION_TOKEN={TEMPORARY ACCESS TOKEN PROVIDED BY AWS SSO}
```

### Running the CDK Tasks

The CDK tasks execution is automated with the help of the `invoke` python package. In order to deploy to the development environment you just need to execute:

```shell script
poetry run invoke deploy
```

After doing all your necessary tests, please remember to clean up the `aws development environment` by executing:

```shell script
poetry run invoke destroy
```

### Running Lambdas Locally

You can run your aws deployments locally using SAM CLI. To install it, follow the [instructions](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html).

## Pre Commit Setup

Pre-commit is a python package that helps us execute validations before we commit any changes. To install the git hook scripts in your local `.git/hooks` folder, you need to execute:

```shell
pre-commit install
```

In order to activate the commitizen git hook you need to additionally execute the following command:

```shell
pre-commit install --hook-type commit-msg
```

When you execute the `git commit` command, the following validations are made:

### Branch name check: 

The commit will fail if the branch name you defined does not comply with the following pattern:

```regexp
(build|ci|docs|feat|fix|perf|refactor|style|test|chore|revert|bump)-SQUAD-\d{2,5}-([\w-]+)$
```

### Code formatting:

If you forgot to run the command `poetry run invoke validate` before commiting, this git hook will fail your commit and then format the code by executing the `black` formatter. If this is the only check that fails, you can retry the commit and it should pass.

### Commit check:

You need to follow the [conventional commit](https://www.conventionalcommits.org/es/v1.0.0-beta.2/) format. A valid commit messages would look something like this:

```
feat: Added login endpoint
fix: corrected validations
ci: added CDK stack, included workflow yaml
docs: updated README
```

The hooks used in this repo are defined in the `.pre-commit-config.yaml` file.

## Packages and Tools

- Http Framework: [FastAPI](https://fastapi.tiangolo.com)
- Http Client: [Httpx](https://www.python-httpx.org)
- Http Server: [Uvicorn](https://www.uvicorn.org/)
- Coverage: [Pytest-Cov](https://pytest-cov.readthedocs.io/en/latest)
- Static type check: [MyPy](https://mypy.readthedocs.io/en/stable/)
- Task manager: [Invoke](http://www.pyinvoke.org/index.html) 
- Multiprocess manager: [Gunicorn](http://docs.gunicorn.org/en/latest/install.html)
- Structured Logging: [Loguru](https://github.com/Delgan/loguru)
- AWS Integration: [AWS Power Tools for Python](https://docs.powertools.aws.dev/lambda/python/latest/)
- IaC: [AWS CDK](https://github.com/aws/aws-cdk)
- Semantic versioning and conventional commits: [Commitizen](https://commitizen-tools.github.io/commitizen/)
- Git hooks: [Pre-commit](https://pre-commit.com)
