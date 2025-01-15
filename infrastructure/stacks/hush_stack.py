from typing import TypedDict

from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
from aws_cdk import (
    aws_lambda,
    aws_apigateway,
    aws_secretsmanager,
    RemovalPolicy,
    Stack,
    Duration,
)
from aws_cdk.aws_secretsmanager import SecretStringGenerator
from cdk_aws_lambda_powertools_layer import LambdaPowertoolsLayer
from constructs import Construct

from .config import (
    DEPENDENCIES_LAYER_DIR,
    LAMBDA_BUILD_DIR,
    LAMBDA_HANDLER_PATH,
    LAMBDA_APP_LAYER,
    LAMBDA_NAME,
    AGW_REST_API_NAME,
    AGW_REST_API_ROOT,
    AGW_REST_API_STAGE,
    POWERTOOLS_LAYER_ID,
    LAMBDA_POWERTOOLS_VERSION,
    SALT_SECRET_NAME,
    PASSPRHASE_SECRET_NAME,
)


class HushLambdaStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs: TypedDict) -> None:
        super().__init__(scope, id, **kwargs)

        salt_secret = aws_secretsmanager.Secret(
            self,
            "SaltSecret",
            secret_name=SALT_SECRET_NAME,
            generate_secret_string=SecretStringGenerator(password_length=16),
        )

        passphrase_secret = aws_secretsmanager.Secret(
            self,
            "PassphraseSecret",
            secret_name=PASSPRHASE_SECRET_NAME,
            generate_secret_string=SecretStringGenerator(password_length=16),
        )

        power_tools_layer = LambdaPowertoolsLayer(
            self,
            POWERTOOLS_LAYER_ID,
            include_extras=True,
            layer_version_name="PowerToolsHush",
            version=LAMBDA_POWERTOOLS_VERSION,
        )
        dependencies_layer = PythonLayerVersion(
            self,
            f"{id}-dependencies",
            entry=DEPENDENCIES_LAYER_DIR,
            compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_12],
            removal_policy=RemovalPolicy.DESTROY,
        )

        app_layer = PythonLayerVersion(
            self,
            f"{id}-app",
            entry=LAMBDA_APP_LAYER,
            compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_12],
            removal_policy=RemovalPolicy.DESTROY,
        )

        secrets_extension = aws_lambda.ParamsAndSecretsLayerVersion.from_version(
            aws_lambda.ParamsAndSecretsVersions.V1_0_103, cache_enabled=True
        )

        base_lambda = aws_lambda.Function(
            self,
            LAMBDA_NAME,
            handler=LAMBDA_HANDLER_PATH,
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            code=aws_lambda.Code.from_asset(LAMBDA_BUILD_DIR),
            layers=[dependencies_layer, app_layer, power_tools_layer],
            params_and_secrets=secrets_extension,
            tracing=aws_lambda.Tracing.ACTIVE,
            environment={
                "SALT_NAME": salt_secret.secret_name,
                "PASSPHRASE_NAME": passphrase_secret.secret_name,
                "POWERTOOLS_SERVICE_NAME": "hush",
                "POWERTOOLS_LOG_LEVEL": "INFO",
                "POWERTOOLS_METRICS_NAMESPACE": "HushLambda",
            },
            timeout=Duration.minutes(1),
        )

        salt_secret.grant_read(base_lambda)
        passphrase_secret.grant_read(base_lambda)

        # create a RestApi resource
        base_api = aws_apigateway.RestApi(
            self,
            AGW_REST_API_NAME,
            rest_api_name=AGW_REST_API_NAME,
            deploy_options=aws_apigateway.StageOptions(
                stage_name=AGW_REST_API_STAGE,
            ),
        )

        ref_arch = base_api.root.add_resource(AGW_REST_API_ROOT)

        # add proxy and points to lambda funcion
        ref_arch.add_proxy(
            default_integration=aws_apigateway.LambdaIntegration(base_lambda),
            default_cors_preflight_options=aws_apigateway.CorsOptions(
                allow_methods=["GET", "POST"],
                allow_origins=aws_apigateway.Cors.ALL_ORIGINS,
            ),
        )
