from aws_cdk import (
    Stack,
    aws_sqs as sqs,
    aws_iam as iam,
    Duration,
)
from constructs import Construct


class SqsStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create SQS Queues
        self.verification_queue = sqs.Queue(
            self, "EmailVerificationQueue", visibility_timeout=Duration.seconds(30)
        )

        self.forgot_password_queue = sqs.Queue(
            self, "ForgotPasswordQueue", visibility_timeout=Duration.seconds(30)
        )

        # Use existing IAM user
        existing_user = iam.User.from_user_name(self, "David", user_name="YcwDavid")

        # Grant permissions to the existing user
        self.verification_queue.grant_send_messages(existing_user)
        self.forgot_password_queue.grant_send_messages(existing_user)
