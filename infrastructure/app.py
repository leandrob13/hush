import os

from aws_cdk import App, Environment

from stacks.config import LAMBDA_STACK_ID
from stacks.ref_arch_stack import RefArchLambdaStack

app = App()
RefArchLambdaStack(
    app,
    LAMBDA_STACK_ID,
    env=Environment(
        account=os.environ["AWS_ACCOUNT_ID"], region=os.environ["AWS_REGION"]
    ),
)

app.synth()
