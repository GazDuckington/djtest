"""Firebase manager"""
import time
from functools import wraps
from decouple import config
from django.http import JsonResponse
from django.shortcuts import redirect
import requests, json
import firebase_admin
from firebase_admin import credentials, db, auth

from .redis import redis_control

FB_API=str(config('FIREBASE_WEB_API'))
FB_CRED=str(config('FIREBASE_ADMIN_CRED'))
FB_DB_URL=str(config('FIREBAS_DB_URL'))
FB_LOGIN_ENDPOINT = (
    "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
)
FB_LOGOUT_ENDPOINT= "https://identitytoolkit.googleapis.com/v1/accounts:signOut"

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
        FB_LOGIN_ENDPOINT,
        params={"key": FB_API},
        data=payload)

    return r.json()


def is_token_valid(token):
    try:
        decoded_token = auth.verify_id_token(token)
        expiration_time = decoded_token.get('exp')
        current_time = int(time.time())
        return expiration_time > current_time
    except Exception:
        return False


def signout():
    token = redis_control.get("user_token")
    if is_token_valid(token):
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token.get('uid')
        user = auth.get_user(user_id)
        try:
            auth.revoke_refresh_tokens(user_id)
            rev_sec = user.tokens_valid_after_timestamp / 1000
            redis_control.delete("user_token")
            print(f"Successfully signed out user with ID: {user_id}, at {rev_sec}")
        except auth.TokenSignError as e:
            print(f"Error revoking tokens for user: {e}")
    else:
        print("Token is expired or invalid.")


def firebase_auth_required(f):
    """Memastikan endpoint hanya dapat diakses jika user sudah login"""
    @wraps(f)
    def _wrapped_view(request, *args, **kwargs):
        authorization_header = redis_control.get("user_token")
        if is_token_valid(authorization_header):
            return f(request, *args, **kwargs)
        request.session["info"] = ""
        request.session["error"] = "error: invalid token"
        return redirect("login")

    return _wrapped_view
