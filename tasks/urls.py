from django.urls import path
from django.views.generic import TemplateView 
from django.contrib.auth import views as auth_views
from . import views 


urlpatterns = [
    path('', views.home),
    path('dashboard-user/', views.dashboard_user, name='dashboard_user'),  
    path('loan-emi/', views.loan_emi, name='loan_emi'),
    path('loan/<int:loan_id>/emi/', views.emi, name='emi'),


    path('dashboard-admin/', views.Admin_dashboard, name='dashboard-admin'),
    path('apply-loan/', views.apply_loan, name='apply_loan'),
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('save-location/', views.save_location),
    path('pay/<int:loan_id>/', views.ssl_payment, name='ssl_payment'),
    path('payment-success/', TemplateView.as_view(template_name='loans/payment_success.html')),
    path('payment-fail/', TemplateView.as_view(template_name='loans/payment_fail.html')),
    path('payment-cancel/', TemplateView.as_view(template_name='loans/payment_fail.html')),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('form/', views.profile_form, name='profile_form'), 
    path('kyc_upload/', views.kyc_upload, name='kyc_upload'), 

    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'), 


    path('ssl-payment/<int:loan_id>/', views.ssl_payment, name='ssl_payment'),
    path('ssl-ipn/', views.ssl_ipn, name='ssl_ipn'),
    path('ssl-success/', views.ssl_success, name='ssl_success'),
    path("receipt/<int:loan_id>/", views.receipt_print, name="receipt_print"),

    path('ssl-fail/', views.ssl_fail, name='ssl_fail'),
    path('ssl-cancel/', views.ssl_cancel, name='ssl_cancel'), 


    #..............................
    #.........Admin Dashboard......
    #..............................


    path('admin/dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('admin/loans/', views.loan_list, name='loan-list'),
    path('admin/loan/<int:loan_id>/', views.loan_detail, name='loan-detail'),
    path('admin/loan/<int:loan_id>/approve/', views.approve_loan, name='approve-loan'),
    path('admin/users/<int:user_id>/assign-role/', views.assign_role, name='assign-role'),
    path('admin/groups/create/', views.Create_Group, name='create-group'),
    path('admin/groups/', views.Group_list, name='group-list'),  


    path('no-permission/', views.no_permission, name='no-permission'),
  

]
 