from django.http import HttpResponse
from django.shortcuts import render

# Le viste base vanno qui.


def index(request):
    print(request)
    return HttpResponse("<b>Yeah</b>")