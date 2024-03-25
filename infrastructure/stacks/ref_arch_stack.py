from typing import TypedDict

from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
from aws_cdk import aws_lambda, aws_apigateway, RemovalPolicy, aws_cognito, Stack
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
    USER_POOL_NAME,
    USER_POOL_CLIENT_NAME,
    USER_POOL_AUTHORIZER_NAME,
    LAMBDA_POWERTOOLS_VERSION,
)


class RefArchLambdaStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs: TypedDict) -> None:
        super().__init__(scope, id, **kwargs)

        user_pool = aws_cognito.UserPool(self, USER_POOL_NAME)
        user_pool.add_client(
            USER_POOL_CLIENT_NAME,
            auth_flows=aws_cognito.AuthFlow(user_password=True),
            supported_identity_providers=[
                aws_cognito.UserPoolClientIdentityProvider.COGNITO
            ],
        )
        authorizer = aws_apigateway.CognitoUserPoolsAuthorizer(
            self, USER_POOL_AUTHORIZER_NAME, cognito_user_pools=[user_pool]
        )

        power_tools_layer = LambdaPowertoolsLayer(
            self,
            POWERTOOLS_LAYER_ID,
            include_extras=True,
            layer_version_name="PowerToolsRefArch",
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

        base_lambda = aws_lambda.Function(
            self,
            LAMBDA_NAME,
            handler=LAMBDA_HANDLER_PATH,
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            code=aws_lambda.Code.from_asset(LAMBDA_BUILD_DIR),
            layers=[dependencies_layer, app_layer, power_tools_layer],
            tracing=aws_lambda.Tracing.ACTIVE,
        )

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
            default_method_options=aws_apigateway.MethodOptions(
                authorization_type=aws_apigateway.AuthorizationType.COGNITO,
                authorizer=authorizer,
                authorization_scopes=["aws.cognito.signin.user.admin"],
            ),
            default_cors_preflight_options=aws_apigateway.CorsOptions(
                allow_methods=["GET", "POST"],
                allow_origins=aws_apigateway.Cors.ALL_ORIGINS,
            ),
        )
