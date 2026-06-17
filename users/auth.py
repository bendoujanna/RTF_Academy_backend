import firebase_admin
from firebase_admin import auth, credentials
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from .models import UserProfile

# initialize the Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)

class FirebaseAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # grab the authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None

        # token is well formatted
        auth_header = auth_header.split()
        if len(auth_header) != 2 or auth_header[0].lower() != 'bearer':
            return None

        id_token = auth_header[1]

        try:
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token.get('uid')
            email = decoded_token.get('email', '')
        except Exception:
            raise AuthenticationFailed('Invalid or expired Firebase token.')

        try:
            user = UserProfile.objects.get(uid=uid)
        except UserProfile.DoesNotExist:
            user = UserProfile.objects.create(
                uid=uid,
                email=email,
                role='Student',
                full_name=email.split('@')[0]
            )

        return (user, None)