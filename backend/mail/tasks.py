from celery import shared_task
from django.core.mail import EmailMessage
from django.conf import settings
from django.core import signing
from user.models import Profile
import string
import os
import boto3
import json
from django.template.loader import render_to_string
from django.contrib.auth.hashers import make_password
import random
import boto3
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_to_sqs(message, queue_url):
    """
    將消息放入 SQS 隊列。
    """
    try:
        sqs_client = boto3.client("sqs", region_name=settings.AWS_REGION)
        sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message),
        )
        return "Message sent to SQS successfully."
    except Exception as e:
        logger.error(f"Error sending message to SQS: {e}")
        raise


@shared_task
def enqueue_email(email, name, token_s, mail_type):
    """
    新增郵件發送請求到 SQS。
    """
    try:
        if mail_type == "verification":  # 信件為驗證信
            message = {
                "email": email,
                "name": name,
                "verification_url": f"{settings.SITE_URL}/user/check/{token_s}",
            }
            send_to_sqs.delay(message, settings.AWS_SQS_VERIFICATION_QUEUE_URL)
        elif mail_type == "forgot_password":  # 信件為新密碼信
            message = {
                "email": email,
                "name": name,
            }
            send_to_sqs.delay(message, settings.AWS_SQS_NEW_PASSWORD_QUEUE_URL)
            print("Email request enqueued successfully.")
        return "Email request enqueued successfully."
    except Exception as e:
        logger.error(f"Failed to enqueue email: {e}")
        raise


@shared_task
def process_verification_email_from_sqs():
    """
    從 SQS 隊列取出消息並發送郵件。
    """
    try:
        # 連接到 SQS
        sqs_client = boto3.client("sqs", region_name=settings.AWS_REGION)
        response = sqs_client.receive_message(
            QueueUrl=settings.AWS_SQS_VERIFICATION_QUEUE_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10,
        )

        messages = response.get("Messages", [])
        if not messages:
            return "No messages to process."

        for message in messages:
            # 解析消息
            body = json.loads(message["Body"])
            email = body["email"]
            name = body["name"]
            verification_url = body["verification_url"]

            # 發送郵件
            html_content = render_to_string(
                "email/verification.html",
                {"name": name, "verification_url": verification_url},
            )
            email_message = EmailMessage(
                subject=f"Welcome to CafeMate, {name}!",
                body=html_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
            )
            email_message.content_subtype = "html"
            email_message.send()

            # 刪除已處理的消息
            sqs_client.delete_message(
                QueueUrl=settings.AWS_SQS_VERIFICATION_QUEUE_URL,
                ReceiptHandle=message["ReceiptHandle"],
            )
            print("Processed messages successfully.")
        logger.info(f"Verification SQS Response: {response}")
        return "Processed messages successfully."
    except Exception as e:
        print(f"Error processing email from SQS: {e}")
        logger.error(f"Error processing email from SQS: {e}")
        raise


@shared_task
def process_forgot_email_from_sqs():
    """
    從 SQS 隊列取出消息並處理忘記密碼郵件。
    """
    try:
        # 連接到 SQS
        sqs_client = boto3.client("sqs", region_name=settings.AWS_REGION)
        try:
            response = sqs_client.receive_message(
                QueueUrl=settings.AWS_SQS_NEW_PASSWORD_QUEUE_URL,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=10,
            )
        except Exception as e:
            logger.error(f"Error receiving message from SQS: {e}")
            raise

        messages = response.get("Messages", [])
        if not messages:
            return "No messages to process."

        for message in messages:
            # 解析消息
            body = json.loads(message["Body"])
            print("Received message:", body)
            email = body["email"]
            name = body["name"]
            # 查找用戶
            user = Profile.objects.get(username=name)

            # 生成新的密碼
            chars = string.ascii_letters + string.digits
            new_pw = "".join(random.sample(chars, 16))
            hashed_pw = make_password(new_pw)

            # 更新用戶密碼
            rows_updated = Profile.objects.filter(username=name).update(
                password=hashed_pw
            )
            if rows_updated == 0:
                raise Exception("Password update failed: No matching user found")

            # 準備發送的郵件內容 (HTML格式)
            context = {
                "username": user.username,
                "new_password": new_pw,
            }
            html_content = render_to_string("email/password_reset.html", context)

            # 發送郵件，設置 HTML 格式
            email_message = EmailMessage(
                subject="CafeMate Password Reset",  # 郵件標題
                body=html_content,  # 郵件內容
                from_email=settings.EMAIL_HOST_USER,  # 發件人信箱
                to=[email],  # 收件人信箱
            )
            email_message.content_subtype = "html"
            email_message.send()

            # 刪除已處理的消息
            sqs_client.delete_message(
                QueueUrl=settings.AWS_SQS_NEW_PASSWORD_QUEUE_URL,
                ReceiptHandle=message["ReceiptHandle"],
            )

        print("Processed forgot email messages successfully.")
        logger.info(f"Forgot Password SQS Response: {response}")
        return "Processed forgot email messages successfully."

    except Exception as e:
        print("Error:", e)
        logger.error(f"Error processing forgot email from SQS: {e}")
        raise


class email_token:
    def generate_token(self, email):  # 加密簽名
        signer = signing.TimestampSigner().sign_object(email)
        return signer

    def confirm_token(self, token):  # Token 永遠有效
        try:
            email = signing.TimestampSigner().unsign_object(
                token
            )  # 解密簽名，獲取 email
            return email
        except signing.BadSignature:
            return None
