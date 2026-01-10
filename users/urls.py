from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.register_account, name='register_user'),
    path('login-user/', views.login_account, name='login_user'), 
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),  
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('profile/', views.register_profile, name='profile'),
    path("bank_verify/", views.Recipient_Account, name="bank_verify"),
]
