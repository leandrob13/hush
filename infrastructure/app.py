import os

from aws_cdk import App, Environment

from stacks.config import LAMBDA_STACK_ID
from stacks.hush_stack import HushLambdaStack

app = App()
HushLambdaStack(
    app,
    LAMBDA_STACK_ID,
    env=Environment(
        account=os.environ["AWS_ACCOUNT_ID"], region=os.environ["AWS_REGION"]
    ),
)

app.synth()
