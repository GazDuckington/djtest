import time
from functools import wraps
from decouple import config
from django.http import JsonResponse
import requests, json
import firebase_admin
from firebase_admin import credentials, db, auth

FB_API=str(config('FIREBASE_WEB_API'))
FB_CRED=str(config('FIREBASE_ADMIN_CRED'))
FB_DB_URL=str(config('FIREBAS_DB_URL'))
FB_LOGIN_API=f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FB_API}"

cred = credentials.Certificate(FB_CRED)

firebase_admin.initialize_app(cred, {
    'databaseURL': FB_DB_URL
})

ref = db.reference('/')


def signin_with_email_and_password(email: str, password: str):
    payload = json.dumps({
        "email": email,
        "password": password,
        "returnSecureToken": True
    })
    r = requests.post(
        FB_LOGIN_API,
        params={"key": FB_API},
        data=payload)

    return r.json()


def firebase_auth_required(f):
    """Memastikan endpoint hanya dapat diakses jika user sudah login"""
    @wraps(f)
    def _wrapped_view(request, *args, **kwargs):
        authorization_header = request.headers.get('Authorization', '')

        try:
            decoded_token = auth.verify_id_token(authorization_header)
            if 'exp' in decoded_token and decoded_token['exp'] >= int(time.time()):
                print("true")
                return f(request, *args, **kwargs)
            else:
                return JsonResponse({"error": "Expired token"}, status=401)
        except Exception:
            return JsonResponse({"error": "Invalid token"}, status=401)

    return _wrapped_view
