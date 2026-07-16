import os
import firebase_admin
from firebase_admin import auth, credentials
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from .models import UserProfile

firebase_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', None)

if not firebase_admin._apps:
    if firebase_path and os.path.exists(firebase_path):
        cred = credentials.Certificate(firebase_path)
        firebase_admin.initialize_app(cred)
    else:
        print("Firebase credentials not found. Skipping initialization.")

class FirebaseAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return None

        id_token = auth_header.split("Bearer ")[1].strip()

        try:
            decoded_token = auth.verify_id_token(id_token)
        except auth.ExpiredIdTokenError:
            raise AuthenticationFailed("Firebase token has expired. Please refresh your session.")
        except auth.InvalidIdTokenError:
            raise AuthenticationFailed("Invalid Firebase token.")
        except auth.RevokedIdTokenError:
            raise AuthenticationFailed("Firebase token has been revoked.")
        except Exception as e:
            raise AuthenticationFailed(f"Firebase authentication error: {str(e)}")

        uid = decoded_token.get('uid')
        email = decoded_token.get('email', '')
        google_name = decoded_token.get('name')

        if not uid:
            raise AuthenticationFailed("Token is missing the uid claim.")

        try:
            user = UserProfile.objects.get(uid=uid)
        except UserProfile.DoesNotExist:

            if email and UserProfile.objects.filter(email=email).exists():
                UserProfile.objects.filter(email=email).update(uid=uid)
                user = UserProfile.objects.get(uid=uid)
            else:
                final_name = google_name if google_name else email.split('@')[0]
                user = UserProfile.objects.create_user(
                    uid=uid,
                    email=email,
                    role='Student',
                    full_name=final_name
                )

        if not user.is_active:
            raise AuthenticationFailed("This account has been deactivated. Please contact support.")

        return (user, None)