from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.register_account, name='register_user'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('profile/', views.register_profile, name='profile'),
    
]
