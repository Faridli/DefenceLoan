from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from .models import LoanApplication,LoanAdmin, OTPVerification, UserDevice, UserVerification
from .forms import UserRegisterForm
import random, json, uuid, requests
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import LoanApplication
from django.views.decorators.cache import never_cache
import uuid
import requests
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings
from .models import LoanApplication  # tasks app এর LoanApplication

def home(request):
    return redirect('dashboard')

@never_cache
# @login_required
def dashboard_user(request):
    loans = LoanApplication.objects.filter(user=request.user).order_by('-id')

    return render(request, 'loans/dashboard_user.html', {
        'loans': loans
    })


# লোন ড্যাশবোর্ড 
@never_cache
@login_required
def Admin_dashboard(request):
    loans = LoanAdmin.objects.filter(user=request.user)
    total = loans.count()
    approved = loans.filter(status='Approved').count()
    pending = loans.filter(status='Pending').count()
    rejected = loans.filter(status='Rejected').count()

    context = {
        'loans': loans,
        'total': total,
        'approved': approved,
        'pending': pending,
        'rejected': rejected
    }
    return render(request, 'admin/dashboard.html', context)

@login_required
def apply_loan(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        months = request.POST.get('months')
        purpose = request.POST.get('purpose')
        basic_salary = request.POST.get('basic_salary')
        bank_name = request.POST.get('bank_name')
        salary_account = request.POST.get('salary_account_number')
        previous_loans = request.POST.get('previous_loans')
        salary_file = request.FILES.get('salary_certificate')

        # Validation
        if not amount or not months:
            return render(request, 'loans/apply_loan.html', {
                'error': 'Amount & Months are required'
            })

        # Convert previous_loans JSON safely
        previous_loans_value = None
        if previous_loans and previous_loans.lower() != 'no':
            try:
                previous_loans_value = json.loads(previous_loans)
            except json.JSONDecodeError:
                previous_loans_value = None

        # LoanApplication save
        loan = LoanApplication.objects.create(
            user=request.user,
            amount=amount,
            monthly_installment=months,
            purpose=purpose,
            basic_salary=basic_salary or None,
            bank_name=bank_name or None,
            salary_account_number=salary_account or None,
            previous_loans=previous_loans_value,
            salary_certificate=salary_file if salary_file else None
        )

        # 🔹 Redirect to bank_verify after saving
        return redirect('bank_verify')

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


import uuid
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import LoanApplication

@login_required
def ssl_payment(request, loan_id):
    loan = get_object_or_404(LoanApplication, id=loan_id, user=request.user)
    
    # Transaction ID generate
    tran_id = str(uuid.uuid4())
    loan.tran_id = tran_id
    loan.save()

    # Payment data
    data = {
        'store_id': settings.SSLCOMMERZ_STORE_ID,
        'store_passwd': settings.SSLCOMMERZ_STORE_PASS,
        'total_amount': float(loan.monthly_installment),
        'currency': 'BDT',
        'tran_id': tran_id,
        'success_url': request.build_absolute_uri('/tasks/ssl-success/'),
        'fail_url': request.build_absolute_uri('/tasks/ssl-fail/'),
        'cancel_url': request.build_absolute_uri('/tasks/ssl-cancel/'),
        'cus_name': request.user.username or request.user.get_full_name(),
        'cus_email': request.user.email,
        'cus_phone': request.user.phone or '01700000000',
    }

    # Request to SSLCommerz (sandbox)
    response = requests.post(settings.SSLCOMMERZ_URL, data=data)
    
    try:
        ssl_data = response.json()
    except ValueError:
        ssl_data = {}

    print("SSL RESPONSE:", ssl_data)  # Debug

    if ssl_data.get("status") == "SUCCESS" and ssl_data.get("GatewayPageURL"):
        return redirect(ssl_data["GatewayPageURL"])
    else:
        return render(request, "loans/payment_error.html", {
            "error": ssl_data.get("failedreason", "Payment gateway rejected the request")
        })




from django.http import HttpResponse
@csrf_exempt
def ssl_ipn(request):
    if request.method == "POST":
        tran_id = request.POST.get("tran_id")
        status = request.POST.get("status")

        try:
            loan = LoanApplication.objects.get(tran_id=tran_id)
            if status == "VALID":
                loan.payment_status = "PAID"
            else:
                loan.payment_status = "FAILED"
            loan.save()
        except LoanApplication.DoesNotExist:
            pass

    return HttpResponse("OK")


@csrf_exempt
def ssl_success(request):
    return render(request, "ssl/success.html")
@csrf_exempt
def ssl_fail(request):
    return render(request, "ssl/fail.html")
@csrf_exempt
def ssl_cancel(request):
    return render(request, "ssl/cancel.html")

# def register(request):
#     if request.method == 'POST':
#         form = UserRegisterForm(request.POST, request.FILES)
#         if form.is_valid():
#             user = form.save()
#             UserVerification.objects.create(
#                 user=user,
#                 nid_image=form.cleaned_data['national_id'],
#                 service_id_image=form.cleaned_data['service_id_card'],
#                 live_photo=form.cleaned_data['live_photo']
#             )
#             from django.contrib.auth import login
#             login(request, user)
#             return redirect('dashboard')
#     else:
#         form = UserRegisterForm()
#     return render(request, 'loans/register.html', {'form': form})

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import UserProfileForm  # আপনার ফর্ম ইম্পোর্ট
# # @login_required
# def profile_view(request):
#     return render(request, 'loans/', {
#         'user': request.user
#     })

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm
# @login_required 
@login_required
def profile_form(request):
    user = request.user

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            action = request.POST.get('action')  # কোন বাটন ক্লিক হলো
            if action == 'save':
                form.save()
                messages.success(request, "Profile saved successfully!")
                return redirect('kyc_upload')  # Save হলে kyc_upload এ
            elif action == 'edit':
                return redirect('profile_update')  # Edit হলে profile_update এ
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'loans/profile_form.html', {'form': form})


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm

@login_required
def profile_update(request):
    user = request.user

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile_view')
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'loans/profile_update.html', {
        'form': form
    })



from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserKycForm


@login_required
def kyc_upload(request):
    user = request.user

    if request.method == 'POST':
        form = UserKycForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Documents uploaded successfully ✅")
            # 🔹 Redirect to apply_loan after saving
            return redirect('apply_loan')
        else:
            messages.error(request, "Please fix the errors below ❌")
    else:
        form = UserKycForm(instance=user)

    return render(request, 'loans/kyc_upload.html', {
        'form': form
    })



# @login_required
# def profile_update(request):
#     if request.method == 'POST':
#         form = UserProfileForm(request.POST, request.FILES, instance=request.user)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Profile updated successfully")
#             return redirect('profile')
#     else:
#         form = UserProfileForm(instance=request.user)

#     return render(request, 'profile.html', {'form': form})
