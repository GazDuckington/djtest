from django.contrib.admin.sites import method_decorator
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.decorators import login_required

from .firebase import signin_with_email_and_password, firebase_auth_required


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
            request.session['error'] = res.get("error")
            return redirect("login")
        request.session['id_token'] = res.get('idToken')
        return JsonResponse(res)


class UserLogin(LoginView):
    def get(self, request):
        error_message = request.session.get('error', None)
        context = {"error": error_message}
        return render(request, "registration/login.html", context)

