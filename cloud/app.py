import os
import aws_cdk as cdk
from cloud.sqs_stack import SqsStack

app = cdk.App()

# Create stacks
sqs_stack = SqsStack(
    app,
    "EmailSystemSqsStack",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
    ),
)

# # Add dependencies
# lambda_stack.add_dependency(sqs_stack)
# lambda_stack.add_dependency(dynamodb_stack)

app.synth()
# If you don't specify 'env', this stack will be environment-agnostic.
# Account/Region-dependent features and context lookups will not work,
# but a single synthesized template can be deployed anywhere.
# Uncomment the next line to specialize this stack for the AWS Account
# and Region that are implied by the current CLI configuration.
# env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
# Uncomment the next line if you know exactly what Account and Region you
# want to deploy the stack to. */
# env=cdk.Environment(account='123456789012', region='us-east-1'),
# For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
