from django.shortcuts import render

# Create your views here.

#/index or null
def index(request):
    return render(request,'index.html')
