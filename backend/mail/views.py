from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .tasks import email_token, send_custom_email


@csrf_exempt
def send_email_view(request):
    if request.method == "POST":  # Handle POST requests
        try:
            data = json.loads(bytes.decode(request.body, "utf-8"))
            email = data["email"]
            name = data["name"]  # Assuming the name is also provided in the request
            token = email_token()
            token_s = token.generate_token(email)
            print("Email:", email)
            print("Name:", name)
            send_custom_email(email, name, token_s)  # Call the task to send the email
            message = {"status": "0", "token": token_s}
        except Exception as e:
            print(e)
            message = {"status": "1", "message": "Error sending email"}

        return JsonResponse(message)
