"""
Custom authentication classes for the messaging app.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from django.conf import settings
import jwt

User = get_user_model()


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication class that works with our custom User model.
    """
    
    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[settings.SIMPLE_JWT['USER_ID_CLAIM']]
        except KeyError:
            raise InvalidToken('Token contained no recognizable user identification')

        try:
            user = User.objects.get(**{settings.SIMPLE_JWT['USER_ID_FIELD']: user_id})
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found', code='user_not_found')

        if not user.is_active:
            raise AuthenticationFailed('User is inactive', code='user_inactive')

        return user


class EmailAuthenticationBackend:
    """
    Custom authentication backend to authenticate using email instead of username.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user using email and password.
        """
        email = kwargs.get('email', username)
        if email is None or password is None:
            return None
            
        try:
            user = User.objects.get(email=email)
            if user.check_password(password) and user.is_active:
                return user
        except User.DoesNotExist:
            return None
        
        return None
    
    def get_user(self, user_id):
        """
        Get user by user_id (UUID in our case).
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class BearerTokenAuthentication(BaseAuthentication):
    """
    Simple token authentication using Bearer tokens.
    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Bearer ".  For example:
        Authorization: Bearer 401f7ac837da42b97f613d789819ff93537bee6a
    """
    keyword = 'Bearer'
    model = None

    def get_model(self):
        if self.model is not None:
            return self.model
        from rest_framework.authtoken.models import Token
        return Token

    def authenticate(self, request):
        auth = self.get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            raise AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise AuthenticationFailed('Invalid token.')

        if not token.user.is_active:
            raise AuthenticationFailed('User inactive or deleted.')

        return (token.user, token)

    def get_authorization_header(self, request):
        """
        Return request's 'Authorization:' header, as a bytestring.
        """
        auth = request.META.get('HTTP_AUTHORIZATION', b'')
        if isinstance(auth, str):
            auth = auth.encode('iso-8859-1')
        return auth

    def authenticate_header(self, request):
        return self.keyword


def jwt_get_username_from_payload_handler(payload):
    """
    Override the default username extraction from JWT payload.
    """
    username = payload.get('email')
    return username