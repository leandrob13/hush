import os

DEPENDENCIES_LAYER_DIR = "build/dependencies_layer/"

LAMBDA_BUILD_DIR = "build/lambdas/"

LAMBDA_APP_LAYER = "build/app_layer/"

LAMBDA_HANDLER_PATH = "lambda_functions.api_lambda.lambda_handler"

LAMBDA_NAME = "hush"

AGW_REST_API_NAME = "hush-rest-api"

AGW_REST_API_ROOT = "hush"

AGW_REST_API_STAGE = os.getenv("API_STAGE_ENV", "dev")

POWERTOOLS_LAYER_ID = "AWSLambdaPowertoolsPythonV2"

LAMBDA_STACK_ID = "hush-lambda-stack"

LAMBDA_POWERTOOLS_VERSION = "2.34.2"

# Secrets

SALT_SECRET_NAME = f"HUSH_SALT_{os.getenv('ENVIRONMENT', 'DEV')}"

PASSPRHASE_SECRET_NAME = f"HUSH_PASSPHRASE_{os.getenv('ENVIRONMENT', 'DEV')}"
