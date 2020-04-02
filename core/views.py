import json
from django.http import JsonResponse
from .forms import UserForm, LoginForm

def signup(request):
    """Processes a signup request."""

    if request.method == "POST":
        data = json.loads(request.body.decode())
        form = UserForm(data)
        if form.is_valid():
            user = form.save()
            return JsonResponse({"message": user.create_jwt()})
        return JsonResponse({"error": dict(form.errors)}, status=422)
    return JsonResponse({"error": "Method not allowed"}, status=405)


def login(request):
    """Processes a login request."""

    if request.method == "POST":
        data = json.loads(request.body.decode())
        form = LoginForm(data)
        user = form.validate_credentials()
        if user:
            return JsonResponse({"message": user.create_jwt()})
        else:
            return JsonResponse({"error": dict(form.errors)}, status=422)
    return JsonResponse({"error": "Method not allowed"}, status=405)