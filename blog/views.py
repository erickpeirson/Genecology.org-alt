from django.shortcuts import render

def home(request):
    context = {
        'nav_active': 'home',
    }
    return render(request, 'blog/base_home.html', context)
