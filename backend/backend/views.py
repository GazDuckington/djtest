from django.http import JsonResponse
from django.views import View


# views here
class IndexView(View):
    def get(self, request):
        return JsonResponse({"message": "hello world"})
