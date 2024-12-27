from django.core.mail import EmailMessage
from django.conf import settings


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
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]

    try:
        email_message = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=from_email,
            to=recipient_list,
        )
        email_message.content_subtype = "html"  # 设置内容为 HTML 格式
        email_message.send()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")
