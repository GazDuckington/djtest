"""Firebase manager"""
import time
from functools import wraps
from decouple import config
from django.http import JsonResponse
from django.shortcuts import redirect
import requests, json
import firebase_admin
from firebase_admin import credentials, db, auth

FB_API=str(config('FIREBASE_WEB_API'))
FB_CRED=str(config('FIREBASE_ADMIN_CRED'))
FB_DB_URL=str(config('FIREBAS_DB_URL'))
FB_LOGIN_API = (
    "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
)

cred = credentials.Certificate(FB_CRED)

firebase_admin.initialize_app(cred, {
    'databaseURL': FB_DB_URL
})

ref = db.reference('/')


def signin_with_email_and_password(email: str, password: str):
    """login firebase menggunakan email dan password"""
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
        if not authorization_header:
            request.session["error"] = ""
            request.session["info"] = "silahkan login terlebih dahulu"
            return redirect("login")

        try:
            decoded_token = auth.verify_id_token(authorization_header)
            if 'exp' in decoded_token and decoded_token['exp'] >= int(time.time()):
                request.session["info"] = ""
                request.session["error"] = None
                return f(request, *args, **kwargs)
            request.session["info"] = ""
            request.session["error"] = "error: expired token"
            return redirect("login")
        except ValueError:
            # return JsonResponse({"error": "Invalid token"}, status=401)
            request.session["info"] = ""
            request.session["error"] = "error: invalid token"
            return redirect("login")

    return _wrapped_view
