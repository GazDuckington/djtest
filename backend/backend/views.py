from django.contrib.admin.sites import method_decorator
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.decorators import login_required


# views here
class IndexView(View):
    @method_decorator(login_required(login_url='login/'))
    def get(self, request):
        return JsonResponse({"message": "hello world"})


class UserLogin(LoginView):
    redirect_authenticated_user = True
    def get_success_url(self):
        return reverse_lazy('index')
