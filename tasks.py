from invoke import task
import os
from shutil import copytree, rmtree


@task
def formatcode(c, check=False):
    print("Running black formatter")
    c.run(f"poetry run black infrastructure{' --check' if check else ''}")
    c.run(f"poetry run black src{' --check' if check else ''}")


@task
def mypy(c):
    print("Running mypy")
    c.run("poetry run mypy infrastructure")
    c.run("poetry run mypy src")


@task
def tests(c):
    print("Running pytest")
    c.run("poetry run pytest src/test --cov=src")
    c.run("poetry run coverage html -i")


@task
def vulture(c):
    print("Running vulture")
    c.run("poetry run vulture src")


@task(vulture, mypy, tests)
def validate(c, check=False):
    formatcode(c, check)
    print("DONE VALIDATING")


@task
def clean(c):
    if os.path.exists("build"):
        rmtree("build")
    if os.path.exists("cdk.out"):
        rmtree("cdk.out")


@task(mypy, clean)
def buildlambda(c):
    print("BUILDING LAMBDA")
    build_lambdas = "build/lambdas/"
    build_app_layer = "build/app_layer/"
    build_dependencies_layer = "build/dependencies_layer"
    source = "src/lambda_functions"
    app_source = "src/app"

    os.makedirs(build_dependencies_layer, exist_ok=True)
    copytree(source, f"{build_lambdas}/lambda_functions", dirs_exist_ok=True)
    copytree(app_source, f"{build_app_layer}/src/app", dirs_exist_ok=True)
    c.run(
        f"poetry export --without=dev,http --format=requirements.txt > {build_dependencies_layer}/requirements.txt"
    )


@task(buildlambda)
def deploy(c):
    c.run("cdk bootstrap")
    c.run("cdk deploy")


@task
def destroy(c):
    c.run("cdk destroy --force")


@task
def runhttp(c):
    c.run("poetry run python -m src.http.main")


@task
def commitizen(c):
    c.run("cz check --commit-msg-file .git/COMMIT_EDITMSG")
