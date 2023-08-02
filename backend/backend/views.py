from django.contrib.admin.sites import method_decorator
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View

from .firebase import signin_with_email_and_password, firebase_auth_required
from .redis import redis_control


# views here
class IndexView(View):
    @method_decorator(firebase_auth_required)
    def get(self, request):
        return JsonResponse({"message": "hello world"})


class LoginBase(View):
    def post(self, request):
        email = request.POST.get("email")
        password = request.POST.get("password")

        res = signin_with_email_and_password(email=email, password=password)
        if res.get("error"):
            request.session["info"] = ""
            request.session["error"] = "invalid email or password"
            return redirect("login")
        redis_control.set("user_token", res.get("idToken"))
        return JsonResponse(redis_control.get("user_token"), safe=False)


class UserLogin(LoginView):
    def get(self, request):
        error_message = request.session.get('error', None)
        info_message = request.session.get('info', None)

        context = {
            "info": info_message
        }

        if error_message:
            context["error"] = error_message

        return render(request, "registration/login.html", context)

