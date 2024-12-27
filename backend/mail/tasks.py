from django.core.mail import EmailMessage
from django.conf import settings
import base64
from django.core import signing


def send_custom_email(email, name):
    subject = f"Welcome, {name}!"
    plain_message = f"Hi {name},\nThank you for joining us!"
    html_message = f"""
    <html>
        <body>
            <h1 style="color: #4CAF50;">Hello, {name}!</h1>
            <p>Thank you for joining our platform. We're excited to have you!</p>
            <p><strong>Stay connected!</strong></p>
            <footer style="margin-top: 20px; font-size: small; color: gray;">
                This is an automated message. Please do not reply.
            </footer>
        </body>
    </html>
    """

    # Generate token for email verification
    token = email_token()
    token_s = token.generate_token(email)
    verification_url = f"/user/check/{token_s}"
    verification_message = f"""
    <html>
        <body>
            <h1 style="color: #4CAF50;">Welcome, {name}!</h1>
            <p>Please click the link below to complete your registration:</p>
            <a href="{verification_url}">Complete Registration</a>
            <footer style="margin-top: 20px; font-size: small; color: gray;">
                This is an automated message. Please do not reply.
            </footer>
        </body>
    </html>
    """

    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]

    try:
        email_message = EmailMessage(
            subject="Account Verification",
            body=html_message,
            from_email=from_email,
            to=recipient_list,
        )
        email_message.content_subtype = "html"  # Set the content type to HTML
        email_message.send()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")


class email_token:
    def generate_token(self, email):
        signer = signing.TimestampSigner()
        return signer.sign(email)

    def confirm_token(self, token):
        try:
            email = signing.TimestampSigner(salt=self.salt).unsign(
                token, max_age=3600
            )  # Optional max_age parameter for expiration
            return email
        except signing.BadSignature:
            return None
