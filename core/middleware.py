import jwt
import time
from django.conf import settings
from django.http import JsonResponse
from .models import User

class AuthenticationMiddleware:
    """Inspects incoming requests and tries to add a user object. If the request
    has a JWT key, and if that decodes successfully, and if it isn't too old,
    and if it points to a valid user - it will be added."""

    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):
        try:
            key = request.META.get("HTTP_AUTHORIZATION")
            token = jwt.decode(key, settings.SECRET_KEY)
            oldest_time = time.time() - (settings.TOKEN_TIMEOUT * 86400)
            assert token["iat"] > oldest_time
            request.user = User.objects.get(id=token["sub"])
        except:
            request.user = None
            
        response = self.get_response(request)

        return response