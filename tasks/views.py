from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from .models import LoanApplication, OTPVerification, UserDevice, UserVerification
from .forms import UserRegisterForm
import random, json, uuid, requests
from datetime import timedelta

def home(request):
    return redirect('dashboard')
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import LoanApplication

@login_required
def dashboard(request):
    loans = LoanApplication.objects.filter(user=request.user).order_by('-id')

    return render(request, 'loans/dashboard.html', {
        'loans': loans
    })

import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import LoanApplication

@login_required
@login_required
def apply_loan(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        months = request.POST.get('months')
        purpose = request.POST.get('purpose')
        basic_salary = request.POST.get('basic_salary')
        salary_account = request.POST.get('salary_account_number')
        previous_loans = request.POST.get('previous_loans')

        if not amount or not months:
            return render(request, 'loans/apply_loan.html', {
                'error': 'Amount & Months are required'
            })

        # ✅ JSON safe handling
        previous_loans_value = None
        if previous_loans and previous_loans.lower() != 'no':
            try:
                previous_loans_value = json.loads(previous_loans)
            except json.JSONDecodeError:
                previous_loans_value = None

        LoanApplication.objects.create(
            user=request.user,
            amount=amount,
            months=months,
            purpose=purpose,
            basic_salary=basic_salary or None,
            salary_account_number=salary_account or None,
            previous_loans=previous_loans_value
        )

        return redirect('dashboard')

    return render(request, 'loans/apply_loan.html')



@login_required
def send_otp(request):
    otp = random.randint(100000, 999999)
    OTPVerification.objects.create(
        user=request.user,
        otp=otp,
        purpose="Loan Approval",
        expires_at=timezone.now() + timedelta(minutes=5)
    )
    send_mail(
        'Loan Verification OTP',
        f'Your OTP is {otp}',
        settings.EMAIL_HOST_USER,
        [request.user.email],
        fail_silently=False
    )
    return redirect('verify_otp')

@login_required
def verify_otp(request):
    if request.method == 'POST':
        input_otp = request.POST.get('otp')
        otp_obj = OTPVerification.objects.filter(user=request.user, is_verified=False, expires_at__gte=timezone.now()).last()
        if otp_obj and str(otp_obj.otp) == input_otp:
            otp_obj.is_verified = True
            otp_obj.save()
            return redirect('dashboard')
    return render(request, 'loans/verify_otp.html')

@login_required
def save_location(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        UserDevice.objects.create(
            user=request.user,
            latitude=data.get('lat'),
            longitude=data.get('lng'),
            device_info=data.get('device')
        )
        return JsonResponse({'status': 'saved'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def ssl_payment(request, loan_id):
    loan = get_object_or_404(LoanApplication, id=loan_id, user=request.user)
    tran_id = str(uuid.uuid4())
    data = {
        'store_id': settings.SSLCOMMERZ_STORE_ID,
        'store_passwd': settings.SSLCOMMERZ_STORE_PASS,
        'total_amount': loan.amount,
        'currency': 'BDT',
        'tran_id': tran_id,
        'success_url': request.build_absolute_uri('/payment-success/'),
        'fail_url': request.build_absolute_uri('/payment-fail/'),
        'cancel_url': request.build_absolute_uri('/payment-cancel/'),
        'cus_name': request.user.username,
        'cus_phone': request.user.phone,
    }
    response = requests.post(settings.SSLCOMMERZ_URL, data=data)
    return redirect(response.json()['GatewayPageURL'])

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            UserVerification.objects.create(
                user=user,
                nid_image=form.cleaned_data['national_id'],
                service_id_image=form.cleaned_data['service_id_card'],
                live_photo=form.cleaned_data['live_photo']
            )
            from django.contrib.auth import login
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'loans/register.html', {'form': form})
