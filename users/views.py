from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, ForgotPasswordForm, ResetPasswordForm
from tasks.models import User


from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import UserRegisterForm
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.views.decorators.cache import never_cache 
from tasks.forms import UserProfileForm 
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator

from users.forms import UserRegisterForm
from tasks.models import User
def register_account(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)   # form already hashed password
            user.is_active = False
            user.save()

            # send activation email
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


from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import redirect
from django.contrib import messages

User = get_user_model()

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Account successfully activated! Log in now.')
        return redirect('login_user')
    else:
        messages.error(request, 'সক্টিভেশন লিঙ্কটি অবৈধ।')
        return redirect('register_user')

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
@never_cache 
def login_account(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        next_url = request.POST.get("next")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                # login(request, user) 
                # Session এ user id রাখুন
                request.session["login_user_id"] = user.id

                # যদি ?next= থাকে, সেখানে যাবে
                if next_url:
                    # return redirect(next_url)
                    request.session["next_url"] = next_url

                # না থাকলে dashboard এ যাবে
                return redirect("otp_login")
            else:
                messages.error(request, "Your account is not activated.")
        else:
            messages.error(request, "Invalid username or password.")

    # GET request এ ?next পাঠানো
    next_url = request.GET.get("next", "")
    return render(request, "accounts/user_login.html", {"next": next_url})


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.utils import timezone
import random

from tasks.models import User, OTPVerification


# =========================
# Step 1: Phone Login → Send OTP
# =========================
@never_cache 

def phone_login(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')

        try:
            # সরাসরি User Model থেকে phone খুঁজুন
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            messages.error(request, "This phone number is not correct/registered.")
            return redirect("dashboard_user")

        # Generate OTP
        otp = str(random.randint(100000, 999999))

        # OTP save
        OTPVerification.objects.create(
            user=user,
            otp=otp,
            purpose="login",
            expires_at=timezone.now() + timezone.timedelta(minutes=2)
        )

        # এখানে আপনার SMS API বসিয়ে পাঠাতে পারবেন
        print("LOGIN OTP:", otp)  # Debug purposes

        # Session এ user id রাখুন
        request.session["login_user_id"] = user.id

        messages.success(request, "OTP sent to your phone.")
        return redirect("otp_verify")

    return render(request, "otp/otp_login.html")


# =========================
# Step 2: Verify OTP → Login
# =========================
@never_cache 

def verify_login_otp(request):
    if request.method == "POST":
        otp = request.POST.get("otp")
        user_id = request.session.get("login_user_id")

        if not user_id:
            messages.error(request, "Session expired. Please login again.")
            return redirect("otp_login")

        try:
            # OTP check: latest, not expired, purpose=login
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

            # Login
            login(request, user)
            messages.success(request, f"Welcome {user.username}!")
            return redirect("dashboard_user")

        except OTPVerification.DoesNotExist:
            messages.error(request, "Invalid or expired OTP.")
            return redirect("verify_otp")

    return render(request, "otp/otp_verify.html")





from django.http import JsonResponse
from django.utils import timezone
import random

@never_cache
def resend_login_otp(request):
    user_id = request.session.get("login_user_id")

    if not user_id:
        return JsonResponse({"status": "error", "message": "Session expired"}, status=400)

    # পুরানো OTP invalid করে দাও
    OTPVerification.objects.filter(
        user_id=user_id,
        purpose="login",
        is_verified=False
    ).update(is_verified=True)

    # নতুন OTP
    new_otp = str(random.randint(100000, 999999))

    OTPVerification.objects.create(
        user_id=user_id,
        otp=new_otp,
        purpose="login",
        expires_at=timezone.now() + timezone.timedelta(minutes=1)
    )

    print("RESENT LOGIN OTP:", new_otp)  # SMS API এখানে বসবে

    return JsonResponse({"status": "success", "message": "OTP resent"})


# =========================
# Browser–1: Register / Update Profile
# =========================
@login_required 
@never_cache 
def register_profile(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = UserRegisterForm(instance=request.user)

    return render(request, 'accounts/register_profile.html', {'form': form})



from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ForgotPasswordForm, ResetPasswordForm

User = get_user_model()


# =========================
# 🔐 Forgot Password
# =========================
@never_cache 
def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            try:
                user = User.objects.get(email=email)
                # Session এ রাখুন
                request.session['reset_email'] = email
                messages.success(request, 'Password reset link ready! Proceed to reset.')
                return redirect('reset_password')

            except User.DoesNotExist:
                messages.error(request, 'No user found with this email.')

    else:
        form = ForgotPasswordForm()

    return render(request, 'accounts/forgot_password.html', {'form': form})


# =========================
# 🔁 Reset Password
# ========================= 
@never_cache 
def reset_password(request):
    email = request.session.get('reset_email')

    if not email:
        messages.error(request, "Reset link invalid or expired. Please try again.")
        return redirect('forgot_password')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
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
                # Session clean up
                del request.session['reset_email']
                return redirect('login_user')
    else:
        form = ResetPasswordForm()

    return render(request, 'accounts/reset_password.html', {'form': form})


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import LoanVerification

@never_cache 
@login_required
def Recipient_Account(request):
    # Check if already submitted
    try:
        verification = LoanVerification.objects.get(user=request.user)
        if verification.submitted:
            return redirect('dashboard_user')  # আগে submit করা থাকলে redirect
    except LoanVerification.DoesNotExist:
        verification = None

    if request.method == "POST":
        bank_name = request.POST.get("bank_name")
        account_name = request.POST.get("account_name")
        account_number = request.POST.get("account_number")
        routing_number = request.POST.get("routing_number")
        declaration = request.POST.get("declaration")

        if not ( bank_name and account_name and account_number and routing_number):
            return render(request, "accounts/bank_verify.html", {"error": "সব তথ্য অবশ্যই পূরণ করতে হবে।"})
        if declaration != "on":
            return render(request, "accounts/bank_verify.html", {"error": "আপনাকে ঘোষণা স্বীকার করতে হবে।"})

        # Save
        if verification is None:
            verification = LoanVerification.objects.create(
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

        return redirect("dashboard_user")  # Success

    return render(request, "accounts/bank_verify.html")

