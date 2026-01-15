from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Registration & Login
    path('register/', views.register_account, name='register_user'),
    path('login-user/', views.login_account, name='login_user'),   
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),  

    #..........otp.........দিয়ে  লগইন
    path('otp-login/', views.phone_login, name='otp_login'),  
    path('otp-verify/', views.verify_login_otp, name='otp_verify'), 
    path("resend-otp/", views.resend_login_otp, name="resend_otp"), 

    # Password Reset
    path('forgot-password/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset_form.html',
        email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt',
        success_url='/users/forgot-password/done/',
    ), name='password_reset'),

    path('forgot-password/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url='/users/reset/done/'
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),

    # User Profile & Bank Verify
    path('profile/', views.register_profile, name='profile'),
    path('bank-verify/', views.Recipient_Account, name='bank_verify'), 
]




# from django.urls import path
# from . import views
# from django.contrib.auth import views as auth_views


# urlpatterns = [
#     path('register/', views.register_account, name='register_user'),
#     path('login-user/', views.login_account, name='login_user'), 
#     path('activate/<uidb64>/<token>/', views.activate, name='activate'),  
      
#      # Password reset views
#     path('users/forgot-password/', auth_views.PasswordResetView.as_view(
#         template_name='accounts/password_reset_form.html',
#         email_template_name='accounts/password_reset_email.html',
#         subject_template_name='accounts/password_reset_subject.txt',
#         success_url='/users/forgot-password/done/',
#     ), name='password_reset'),

#     path('users/forgot-password/done/', auth_views.PasswordResetDoneView.as_view(
#         template_name='accounts/password_reset_done.html'
#     ), name='password_reset_done'),

#     path('users/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
#         template_name='accounts/password_reset_confirm.html',
#         success_url='/users/reset/done/'
#     ), name='password_reset_confirm'),

#     path('users/reset/done/', auth_views.PasswordResetCompleteView.as_view(
#         template_name='accounts/password_reset_complete.html'
#     ), name='password_reset_complete'),

#     path('profile/', views.register_profile, name='profile'),
#     path("bank_verify/", views.Recipient_Account, name="bank_verify"),
# ]
