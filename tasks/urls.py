from django.urls import path
from django.views.generic import TemplateView 
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('apply-loan/', views.apply_loan, name='apply_loan'),
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('save-location/', views.save_location),
    path('pay/<int:loan_id>/', views.ssl_payment, name='ssl_payment'),
    path('payment-success/', TemplateView.as_view(template_name='loans/payment_success.html')),
    path('payment-fail/', TemplateView.as_view(template_name='loans/payment_fail.html')),
    path('payment-cancel/', TemplateView.as_view(template_name='loans/payment_fail.html')),
    path('register/', views.register, name='register'), 

    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),

]
