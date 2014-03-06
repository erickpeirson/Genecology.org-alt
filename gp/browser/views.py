from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Yup");
    
def geographic(request):
    return render(request, 'browser/geographic.html')