from django.shortcuts import render, redirect
from django.contrib.auth import logout 
from django.views.decorators.cache import never_cache
# Create your views here.

def home(request):
    return render(request, "home.html")  

def homebase(request):
    return render(request, "homebase.html") 


@never_cache
def logout_view(request):
    # ইউজারকে লগআউট করা
    logout(request)
    # লগআউট হওয়ার পরে সুন্দর লগআউট পেজ দেখানো
    return render(request, 'logout/logout.html')

def no_permission(request): 
    return render(request,'no_permission.html')