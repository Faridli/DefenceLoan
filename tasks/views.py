import json
import random
import uuid
from decimal import Decimal
from datetime import timedelta

import requests
from django.http import JsonResponse,HttpResponse 
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import get_user_model 
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import (
    LoanApplication, LoanAdmin, OTPVerification, UserDevice, UserVerification, InterestRate,AutoDebit
)
from .forms import UserRegisterForm, UserProfileForm, UserKycForm, AssignRoleForm, CreateGroupForm


User = get_user_model()


# =====================================
# Home & User Dashboard
# =====================================
def home(request):
    return redirect('dashboard')


@never_cache
@login_required
def dashboard_user(request):
    loans = LoanApplication.objects.filter(user=request.user).order_by('-id')
    return render(request, 'loans/dashboard_user.html', {'loans': loans})


@login_required
def loan_emi(request):
    loans = LoanApplication.objects.filter(user=request.user).order_by('-id')

    for loan in loans:
        loan.total_payable = loan.total_payable or 0
        loan.total_paid = loan.total_paid or 0
        loan.monthly_installment = loan.monthly_installment or 0
        loan.remaining = loan.remaining_amount
        loan.months = loan.months_paid

    return render(request, "loans/loan_emi.html", {"loans": loans})


@login_required
def emi(request, loan_id):
    loan = get_object_or_404(LoanApplication, id=loan_id, user=request.user)
    context = {
        "loan": loan,
        "months_paid": loan.months_paid(),
        "months_left": loan.duration_months - loan.months_paid(),
    }
    return render(request, "loans/emi.html", context)


# =====================================
# Admin Dashboard
# =====================================
@never_cache
@login_required
def Admin_dashboard(request):
    loans = LoanAdmin.objects.filter(user=request.user)
    context = {
        'loans': loans,
        'total': loans.count(),
        'approved': loans.filter(status='Approved').count(),
        'pending': loans.filter(status='Pending').count(),
        'rejected': loans.filter(status='Rejected').count()
    }
    return render(request, 'admin/dashboard.html', context)


@user_passes_test(lambda u: u.is_superuser, login_url='no-permission')
def admin_dashboard(request):
    context = {
        "total_loans": LoanApplication.objects.count(),
        "pending_loans": LoanApplication.objects.filter(status='Pending').count(),
        "approved_loans": LoanApplication.objects.filter(status='Approved').count(),
        "rejected_loans": LoanApplication.objects.filter(status='Rejected').count(),
        "cleared_loans": LoanApplication.objects.filter(status='Cleared').count(),
    }
    return render(request, 'admin/dashboard.html', context)


# =====================================
# Loan Management (User)
# =====================================
@never_cache
@login_required
def apply_loan(request):
    error = None
    amount_input = request.GET.get('amount') or ''
    duration_input = request.GET.get('duration_months') or ''
    monthly_installment = total_payable = total_interest = None

    # Loan Calculator
    if request.method == 'GET' and amount_input and duration_input:
        try:
            amount = Decimal(amount_input)
            months = int(duration_input)
            active_rate = InterestRate.objects.filter(is_active=True).first()

            if not active_rate:
                error = "No active interest rate is set by admin."
            else:
                rate = Decimal(active_rate.rate)
                yearly_interest = (amount * rate) / Decimal("100")
                total_interest = (yearly_interest / Decimal("12")) * months
                total_payable = amount + total_interest
                monthly_installment = total_payable / months
        except Exception:
            error = "Invalid input for loan calculation."

    # Save Loan Application
    if request.method == 'POST':
        purpose = request.POST.get('purpose')
        basic_salary = request.POST.get('basic_salary') or None
        account_name = request.POST.get('account_name') or None
        bank_name = request.POST.get('bank_name') or None
        salary_account_number = request.POST.get('salary_account_number') or None
        previous_loans = request.POST.get('previous_loans') or None
        salary_certificate = request.FILES.get('salary_certificate')

        try:
            amount = Decimal(request.GET.get('amount'))
            duration_months = int(request.GET.get('duration_months'))
        except:
            error = "Amount and Duration are required from Calculator."

        if not error:
            previous_loans_value = None
            if previous_loans and previous_loans.lower() != 'no':
                try:
                    previous_loans_value = json.loads(previous_loans)
                except json.JSONDecodeError:
                    previous_loans_value = None

            try:
                loan = LoanApplication.objects.create(
                    user=request.user,
                    amount=amount,
                    duration_months=duration_months,
                    purpose=purpose,
                    basic_salary=basic_salary,
                    account_name=account_name,
                    bank_name=bank_name,
                    salary_account_number=salary_account_number,
                    previous_loans=previous_loans_value,
                    salary_certificate=salary_certificate
                )
                return redirect('bank_verify')
            except ValidationError as e:
                error = e

    context = {
        'error': error,
        'amount_input': amount_input,
        'duration_input': duration_input,
        'monthly_installment': monthly_installment,
        'total_payable': total_payable,
        'total_interest': total_interest
    }
    return render(request, 'loans/apply_loan.html', context)


# =====================================
# OTP Verification
# =====================================
@never_cache
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
        otp_obj = OTPVerification.objects.filter(
            user=request.user, is_verified=False, expires_at__gte=timezone.now()
        ).last()
        if otp_obj and str(otp_obj.otp) == input_otp:
            otp_obj.is_verified = True
            otp_obj.save()
            return redirect('dashboard')
    return render(request, 'loans/verify_otp.html')


# =====================================
# User Device & Location
# =====================================
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


# =====================================
# SSL Payment
# ===================================== 
import uuid
import requests
from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import LoanApplication

@login_required
def ssl_payment(request, loan_id):
    # 🔥 view hit
    print("🔥 ssl_payment v4 HIT 🔥")

    # 1️⃣ Get loan
    loan = get_object_or_404(LoanApplication, id=loan_id, user=request.user)
    today = date.today()

    # 2️⃣ Check if already paid this month
    force = request.POST.get("force") == "yes"
    if not force and loan.last_payment_date and loan.last_payment_date.year == today.year and loan.last_payment_date.month == today.month:
        return render(request, "loans/payment_already.html", {
            "loan": loan,
            "message": "এই মাসের কিস্তি ইতিমধ্যে পরিশোধ করা হয়েছে।"
        })

    # 3️⃣ New transaction ID
    tran_id = str(uuid.uuid4())
    loan.tran_id = tran_id
    loan.save(update_fields=["tran_id"])

    # 4️⃣ Prepare SSLCommerz v4 payload
    data = {
        "store_id": settings.SSLCOMMERZ_STORE_ID,
        "store_passwd": settings.SSLCOMMERZ_STORE_PASS,
        "total_amount": float(loan.monthly_installment),
        "currency": "BDT",
        "tran_id": tran_id,
        "product_name": f"Loan Payment #{loan.id}",
        "product_category": "Loan",
        "product_profile": "general",
        "cus_name": request.user.get_full_name() or request.user.username,
        "cus_email": request.user.email or "test@example.com",
        "cus_add1": "Dhaka",
        "cus_city": "Dhaka",
        "cus_postcode": "1207",
        "cus_country": "Bangladesh",
        "cus_phone": getattr(request.user, "phone", "01700000000"),
        "shipping_method": "NO",
        "ship_name": request.user.get_full_name() or "Customer",
        "ship_add1": "Dhaka",
        "ship_city": "Dhaka",
        "ship_postcode": "1207",
        "ship_country": "Bangladesh",
        "success_url": request.build_absolute_uri(f"/tasks/ssl-success/{loan.id}/"),
        "fail_url": request.build_absolute_uri(f"/tasks/ssl-fail/{loan.id}/"),
        "cancel_url": request.build_absolute_uri(f"/tasks/ssl-cancel/{loan.id}/"),
        "value_a": str(loan.id),  # Optional: to identify loan in success callback
    }

    # 5️⃣ Post request to SSLCommerz v4
    try:
        print("Posting to:", settings.SSLCOMMERZ_URL)
        print("Payload:", data)

        response = requests.post(settings.SSLCOMMERZ_URL, data=data, timeout=30)
        response.raise_for_status()
        ssl_data = response.json()

        print("SSL Response:", ssl_data)

    except Exception as e:
        ssl_data = {}
        print("SSL Error:", e)

    # 6️⃣ Redirect to Gateway
    if ssl_data.get("status") == "SUCCESS" and ssl_data.get("GatewayPageURL"):
        print("Redirecting to Gateway:", ssl_data["GatewayPageURL"])
        return redirect(ssl_data["GatewayPageURL"])
    else:
        return render(request, "loans/payment_error.html", {
            "loan": loan,
            "error": ssl_data.get("failedreason", "Payment gateway rejected the request")
        })


@csrf_exempt 
@login_required
def ssl_ipn(request):
    if request.method == "POST":
        tran_id = request.POST.get("tran_id")
        status = request.POST.get("status")
        paid_amount = request.POST.get("amount")

        try:
            loan = LoanApplication.objects.get(tran_id=tran_id)

            if status == "VALID" and paid_amount:
                loan.total_paid = (loan.total_paid or Decimal("0.00")) + Decimal(paid_amount)
                loan.payment_status = "PAID"
            else:
                loan.payment_status = "FAILED"

            loan.save()
        except LoanApplication.DoesNotExist:
            pass

    return HttpResponse("OK")
from decimal import Decimal
from django.shortcuts import get_object_or_404, render
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import LoanApplication

@csrf_exempt
def ssl_success(request, loan_id=None):
    """
    SSLCommerz success callback view
    """
    # Get loan: first try URL parameter, fallback to value_a or tran_id
    loan = None
    if loan_id:
        loan = get_object_or_404(LoanApplication, id=loan_id)
    else:
        # fallback: use tran_id or value_a from POST
        tran_id = request.POST.get("tran_id")
        value_a = request.POST.get("value_a")  # often used to pass loan_id
        loan = LoanApplication.objects.filter(id=value_a).first() or \
               LoanApplication.objects.filter(tran_id=tran_id).first()
        if not loan:
            return render(request, "ssl/error.html", {"error": "Loan not found"})

    # Check for duplicate payment this month
    today = timezone.now().date()
    # if loan.last_payment_date and loan.last_payment_date.year == today.year and loan.last_payment_date.month == today.month:
    #     return render(request, "ssl/error.html", {"error": "এই মাসের কিস্তি ইতিমধ্যে পরিশোধ করা হয়েছে।"})
    if loan.payment_status == "PAID":
        return render(request, "ssl/error.html", {"error": "এই লোনটি সম্পূর্ণ পরিশোধ করা হয়েছে।"})

    # Update loan inside a transaction
    amount = Decimal(request.POST.get("amount", "0.00"))
    with transaction.atomic():
        loan.total_paid += amount
        loan.last_payment_date = today
        if loan.total_paid >= loan.total_payable:
            loan.total_paid = loan.total_payable
            loan.status = "Cleared"
            loan.payment_status = "PAID"
        else:
            loan.payment_status = "PENDING"
        loan.save()

    # Render success page
    return render(request, "ssl/success.html", {
        "loan": loan,
        "total_paid": loan.total_paid,
        "months_paid": loan.months_paid,
        "remaining_amount": loan.remaining_amount,
    })


@csrf_exempt
@login_required
def receipt_print(request, loan_id):
    loan = get_object_or_404(LoanApplication, id=loan_id)
    context = {
        "loan": loan,
        "total_paid": loan.total_paid,
        "months_paid": loan.months_paid,
        "remaining_amount": loan.remaining_amount,
    }
    return render(request, "ssl/receipt.html", context)


@csrf_exempt
def ssl_fail(request):
    return render(request, "ssl/fail.html")


@csrf_exempt
def ssl_cancel(request):
    return render(request, "ssl/cancel.html")


# =====================================
# User Profile & KYC
# =====================================
@login_required
def profile_form(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            action = request.POST.get('action')
            if action == 'save':
                form.save()
                messages.success(request, "Profile saved successfully!")
                return redirect('kyc_upload')
            elif action == 'edit':
                return redirect('profile_update')
    else:
        form = UserProfileForm(instance=user)
    return render(request, 'loans/profile_form.html', {'form': form})


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
    return render(request, 'loans/profile_update.html', {'form': form})


@login_required
def kyc_upload(request):
    user = request.user
    if request.method == 'POST':
        form = UserKycForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Documents uploaded successfully ✅")
            return redirect('apply_loan')
        else:
            messages.error(request, "Please fix the errors below ❌")
    else:
        form = UserKycForm(instance=user)
    return render(request, 'loans/kyc_upload.html', {'form': form})


# =====================================
# Admin User & Loan Management
# =====================================
@user_passes_test(lambda u: u.is_superuser, login_url='no-permission')
def loan_list(request):
    loans = LoanApplication.objects.select_related('user').all()
    return render(request, 'admin/loan_list.html', {"loans": loans})


@user_passes_test(lambda u: u.is_superuser, login_url='no-permission')
def loan_detail(request, loan_id):
    loan = get_object_or_404(LoanApplication, id=loan_id)
    return render(request, 'admin/loan_detail.html', {"loan": loan})


@user_passes_test(lambda u: u.is_superuser, login_url='no-permission')
@user_passes_test(lambda u: u.is_superuser, login_url='no-permission')
def all_loans(request):

    if request.method == 'POST':
        loan_id = request.POST.get('loan_id')
        status = request.POST.get('status')

        loan = get_object_or_404(LoanApplication, id=loan_id)

        # 🔒 Fully paid হলে status change করা যাবে না
        if loan.display_status == 'Cleared':
            # যদি লোন already cleared, কিছু change হবে না
            return redirect('all_loan')

        # 🔒 Approved হলে Cleared না হওয়া পর্যন্ত status change হবে না
        if loan.status == 'Approved' and loan.display_status != 'Cleared':
            return redirect('all_loan')

        # ✅ অন্য সব ক্ষেত্রে status update করা যাবে
        loan.status = status
        loan.save()

        return redirect('all_loan')

    loans = LoanApplication.objects.select_related('user').all().order_by('-id')
    return render(request, 'admin/all_loans.html', {'loans': loans})


@user_passes_test(lambda u: u.is_superuser, login_url='no-permission')
def assign_role(request, user_id):
    user = get_object_or_404(User, id=user_id)
    form = AssignRoleForm()
    if request.method == 'POST':
        form = AssignRoleForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('role')
            user.groups.clear()
            user.groups.add(role)
            messages.success(request, f"{user.username} has been assigned to {role.name}")
            return redirect('admin-dashboard')
    return render(request, 'admin/assign_role.html', {"form": form, "user": user})


@user_passes_test(lambda u: u.is_superuser, login_url='no-permission')
def Create_Group(request):
    form = CreateGroupForm()
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            messages.success(request, f"Group {group.name} created successfully")
            return redirect('create-group')
    return render(request, 'admin/create_group.html', {"form": form})


@user_passes_test(lambda u: u.is_superuser, login_url='no-permission')
def Group_list(request):
    groups = Group.objects.prefetch_related('permissions').all()
    return render(request, 'admin/group_list.html', {"groups": groups})


@staff_member_required
def user_list(request):
    users = User.objects.all()
    return render(request, 'admin/user_list.html', {'users': users})


@user_passes_test(lambda u: u.is_superuser, login_url='no-permission')
def all_users_loans_dashboard(request):
    loans = LoanApplication.objects.select_related('user').order_by('-id')
    return render(request, 'admin/all_users_loans_dashboard.html', {'loans': loans})

@never_cache
def no_permission(request): 
    return render(request, 'admin/no_permission.html')


@user_passes_test(lambda u: u.is_superuser, login_url='no-permission')
def user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    loans = LoanApplication.objects.filter(user=user).order_by('-created_at')
    verification = UserVerification.objects.filter(user=user).first()
    context = {'user': user, 'loans': loans, 'verification': verification}
    return render(request, 'admin/user_profile.html', context)


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
# @login_required
def create_auto_debit(request):
    if request.method == "POST":
        amount = request.POST.get("amount")
        months = request.POST.get("months")
        agree = request.POST.get("agree")

        if not agree:
            messages.error(request, "সম্মতি ছাড়া Auto-Debit চালু করা যাবে না")
            return redirect("auto_debit_create")

        AutoDebit.objects.create(
            user=request.user,
            amount=amount,
            months=months,
            start_date=date.today(),
            next_payment_date=date.today(),
            is_active=True,
            gateway_reference="TEMP_REF_123"  # gateway success হলে real ref
        )

        messages.success(request, "Auto-Debit সফলভাবে চালু হয়েছে")
        return redirect("auto_debit_list")

    return render(request, "auto_debit/auto_debit_form.html")

# ==============================
# Auto-Debit List
# ==============================
# @login_required
def auto_debit_list(request):
    auto_debits = AutoDebit.objects.filter(user=request.user)
    return render(
        request,
        "auto_debit/auto_debit_list.html",
        {"auto_debits": auto_debits}
    )

# ==============================
# Cancel Auto-Debit
# ==============================
import requests
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404

# @login_required
def cancel_auto_debit(request, debit_id):
    if request.method != "POST":
        messages.error(request, "Invalid request")
        return redirect("dashboard_user")

    debit = get_object_or_404(
        AutoDebit,
        id=debit_id,
        user=request.user,
        is_active=True
    )

    cancel_url = f"{settings.SSLCOMMERZ_URL}/validator/api/merchantTransIDvalidationAPI.php"

    payload = {
        "store_id": settings.SSLCOMMERZ_STORE_ID,
        "store_passwd": settings.SSLCOMMERZ_STORE_PASS,
        "reference_no": debit.gateway_reference,
        "action": "cancel",
        "format": "json",
    }

    try:
        response = requests.post(cancel_url, data=payload, timeout=15)
        result = response.json()

        if result.get("APIConnect") == "DONE" and result.get("status") == "SUCCESS":
            debit.is_active = False
            debit.save(update_fields=["is_active"])
            messages.success(request, "Auto-Debit সফলভাবে বন্ধ হয়েছে ✅")
        else:
            messages.error(request, f"Gateway cancel ব্যর্থ ❌ ({result})")

    except requests.RequestException:
        messages.error(request, "Gateway connection সমস্যা ⚠️")

    return redirect("auto_debit_list")



