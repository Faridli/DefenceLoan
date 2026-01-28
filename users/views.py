# =========================
# Imports  Farid9818@
# =========================

from decimal import Decimal
import random

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login,
    get_user_model,
)
from django.contrib.auth import get_user_model 
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.contrib.auth.models import User,Group 
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone 
from tasks.models import User
from django.utils.encoding import force_bytes
from django.utils.http import (
    urlsafe_base64_encode,
    urlsafe_base64_decode,
)
from django.views.decorators.cache import never_cache

from users.forms import (
    UserRegisterForm,
    ForgotPasswordForm,
    ResetPasswordForm,
)
from tasks.forms import UserProfileForm
from tasks.models import (
    User as TaskUser,
    OTPVerification,
    LoanApplication,
    InterestRate,
)
from .models import LoanVerification
from users.forms import LoanApplyForm


def is_client(request):
    return request.user.is_authenticated and request.user.role == 'client'

# =========================
# User Registration
# =========================
# লাগবে না
def register_account(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # Send activation email
            current_site = get_current_site(request)
            mail_subject = 'Activate your account'
            message = render_to_string('accounts/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            EmailMessage(mail_subject, message, to=[user.email]).send()
            messages.success(request, "Check your email to activate account")
            return redirect('login_user')
    else:
        form = UserRegisterForm()

    return render(request, 'accounts/register_account.html', {'form': form})


# =========================
# Account Activation
# =========================

UserModel = get_user_model()


@never_cache
@login_required
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Account successfully activated! Log in now.')
        return redirect('login_user')
    else:
        messages.error(request, 'সক্টিভেশন লিঙ্কটি অবৈধ।')
        return redirect('register_user')


# =========================
# Username / Password Login (Step 0)
# =========================
# লাগবে না।
# @user_passes_test(lambda u: u.is_client, login_url='no-permission')
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

def login_account(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        next_url = request.POST.get("next")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                # অ্যাডমিন হলে সরাসরি লগইন
                if user.is_superuser:
                    login(request, user)
                    return redirect("admin-dashboard")  # সরাসরি অ্যাডমিন ড্যাশবোর্ড

                # সাধারণ ব্যবহারকারীর জন্য OTP লগইন
                request.session["login_user_id"] = user.id
                if next_url:
                    request.session["next_url"] = next_url
                return redirect("otp_login")
            else:
                messages.error(request, "Your account is not activated.")
        else:
            messages.error(request, "Invalid username or password.")

    next_url = request.GET.get("next", "")
    return render(request, "accounts/user_login.html", {"next": next_url})


# =========================
# OTP Login – Step 1 (Send OTP)
# =========================
# লাগবে না
def otp_login(request):
    if request.method == "POST":
        phone = request.POST.get("phone")

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            messages.error(request, "এই ফোন নম্বরের সাথে কোনো একাউন্ট নেই")
            return redirect("otp_login")

        if not user.email:
            messages.error(request, "এই একাউন্টে কোনো ইমেইল যুক্ত নেই")
            return redirect("otp_login")

        OTPVerification.objects.filter(
            user=user,
            purpose="login",
            is_verified=False
        ).update(is_verified=True)

        otp = str(random.randint(100000, 999999))

        OTPVerification.objects.create(
            user=user,
            otp=otp,
            purpose="login",
            expires_at=timezone.now() + timezone.timedelta(minutes=4)
        )

        request.session["login_user_id"] = user.id

        user.email_user(
            subject="Your Login OTP",
            message=f"""
Hello {user.username},

Your login OTP is: {otp}

This OTP is valid for 2 minute.
If you did not request this, please ignore this email.
"""
        )

        messages.success(request, "OTP আপনার ইমেইলে পাঠানো হয়েছে")
        return redirect("otp_verify")

    return render(request, "otp/otp_login.html")


# =========================
# OTP Login – Step 2 (Verify OTP)
# =========================

# লাগবে না 
# @user_passes_test(is_client, login_url='admin/no-permission.html')
def verify_login_otp(request):
    if request.method == "POST":
        otp = request.POST.get("otp")
        user_id = request.session.get("login_user_id")

        if not user_id:
            messages.error(request, "Session expired. Please login again.")
            return redirect("otp_login")

        try:
            otp_record = OTPVerification.objects.filter(
                user_id=user_id,
                otp=otp,
                purpose="login",
                is_verified=False,
                expires_at__gte=timezone.now()
            ).latest("created_at")

            otp_record.is_verified = True
            otp_record.save()

            user = otp_record.user

            if not user.is_active:
                messages.error(request, "Your account is not activated.")
                return redirect("otp_login")

            login(request, user)

            next_url = request.GET.get("next") or request.session.get("next")
            if next_url:
                return redirect(next_url)

            return redirect("dashboard_user")

        except OTPVerification.DoesNotExist:
            messages.error(request, "Invalid or expired OTP.")
            return redirect("verify_otp")

    return render(request, "otp/otp_verify.html")


# =========================
# OTP Login – Step 3 (Resend OTP)
# =========================


# লাগবে না
def resend_login_otp(request):
    user_id = request.session.get("login_user_id")

    if not user_id:
        return JsonResponse({"status": "error", "message": "Session expired"}, status=400)

    user = User.objects.get(id=user_id)

    OTPVerification.objects.filter(
        user=user,
        purpose="login",
        is_verified=False
    ).update(is_verified=True)

    otp = str(random.randint(100000, 999999))

    OTPVerification.objects.create(
        user=user,
        otp=otp,
        purpose="login",
        expires_at=timezone.now() + timezone.timedelta(minutes=1)
    )

    user.email_user(
        subject="Resent Login OTP",
        message=f"Your new OTP is {otp}. Valid for 3 minute."
    )

    return JsonResponse({"status": "success"})


# =========================
# Register / Update Profile
# =========================

@login_required
@never_cache
def register_profile(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('dashboard_user')
    else:
        form = UserRegisterForm(instance=request.user)

    return render(request, 'accounts/register_profile.html', {'form': form})


# =========================
# Forgot Password
# =========================


@never_cache
# @login_required লাগবেন না।
def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            try:
                user = UserModel.objects.get(email=email)
                request.session['reset_email'] = email
                messages.success(request, 'Password reset link ready! Proceed to reset.')
                return redirect('reset_password')
            except UserModel.DoesNotExist:
                messages.error(request, 'No user found with this email.')
    else:
        form = ForgotPasswordForm()

    return render(request, 'accounts/forgot_password.html', {'form': form})


# =========================
# Reset Password
# =========================

# লাগবে না
def reset_password(request):
    email = request.session.get('reset_email')

    if not email:
        messages.error(request, "Reset link invalid or expired. Please try again.")
        return redirect('forgot_password')

    try:
        user = UserModel.objects.get(email=email)
    except UserModel.DoesNotExist:
        messages.error(request, "User not found. Please try again.")
        return redirect('forgot_password')

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']

            if password != confirm_password:
                messages.error(request, "Passwords do not match!")
            else:
                user.set_password(password)
                user.save()
                messages.success(request, "Password successfully reset! You can now login.")
                del request.session['reset_email']
                return redirect('login_user')
    else:
        form = ResetPasswordForm()

    return render(request, 'accounts/reset_password.html', {'form': form})


# =========================
# Bank / Recipient Account Verification
# =========================

@never_cache
@login_required
def Recipient_Account(request):
    try:
        verification = LoanVerification.objects.get(user=request.user)
        if verification.submitted:
            return redirect('dashboard_user')
    except LoanVerification.DoesNotExist:
        verification = None

    if request.method == "POST":
        bank_name = request.POST.get("bank_name")
        account_name = request.POST.get("account_name")
        account_number = request.POST.get("account_number")
        routing_number = request.POST.get("routing_number")
        declaration = request.POST.get("declaration")

        if not (bank_name and account_name and account_number and routing_number):
            return render(request, "accounts/bank_verify.html", {
                "error": "সব তথ্য অবশ্যই পূরণ করতে হবে।"
            })

        if declaration != "on":
            return render(request, "accounts/bank_verify.html", {
                "error": "আপনাকে ঘোষণা স্বীকার করতে হবে।"
            })

        if verification is None:
            LoanVerification.objects.create(
                user=request.user,
                bank_name=bank_name,
                account_name=account_name,
                account_number=account_number,
                routing_number=routing_number,
                declaration_accepted=True,
                submitted=True
            )
        else:
            verification.bank_name = bank_name
            verification.account_name = account_name
            verification.account_number = account_number
            verification.routing_number = routing_number
            verification.declaration_accepted = True
            verification.submitted = True
            verification.save()

        return redirect("dashboard_user")

    return render(request, "accounts/bank_verify.html")


# =========================
# Interest Rate & Loan Apply
# =========================

@never_cache
# @login_required লাগবে না।
def Interest_rate(request):
    active_rate = InterestRate.objects.filter(is_active=True).first()
    interest_rate = active_rate.rate if active_rate else Decimal("12.00")

    monthly_installment = None
    total_payable = None
    total_interest = None

    if request.method == "POST":
        form = LoanApplyForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.user = request.user
            loan.interest_rate = interest_rate
            loan.save()
            return redirect('dashboard_user')
    else:
        form = LoanApplyForm()

    amount = request.GET.get("amount")
    duration = request.GET.get("duration_months")

    if amount and duration:
        try:
            amount = Decimal(amount)
            duration = int(duration)
            yearly_interest = (amount * interest_rate) / Decimal("100")
            total_interest = (yearly_interest / 12) * duration
            total_payable = amount + total_interest
            monthly_installment = total_payable / duration
        except Exception:
            amount = duration = None

    context = {
        "form": form,
        "active_rate": interest_rate,
        "monthly_installment": monthly_installment,
        "total_payable": total_payable,
        "total_interest": total_interest,
        "amount_input": amount,
        "duration_input": duration,
    }

    return render(request, "interest_rate/rate.html", context)












