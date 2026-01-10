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

def register_account(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # ইউজারকে প্রথমে deactivate রাখো
            user.save()

            # Email verification
            current_site = get_current_site(request)
            mail_subject = 'Activate your account'
            message = render_to_string('accounts/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            email = EmailMessage(mail_subject, message, to=[user.email])
            email.send()

            messages.success(request, 'Please confirm your email to complete registration.')
            return redirect('login_user')  # Login page
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
                login(request, user)

                # যদি ?next= থাকে, সেখানে যাবে
                if next_url:
                    return redirect(next_url)

                # না থাকলে dashboard এ যাবে
                return redirect("dashboard_user")
            else:
                messages.error(request, "Your account is not activated.")
        else:
            messages.error(request, "Invalid username or password.")

    # GET request এ ?next পাঠানো
    next_url = request.GET.get("next", "")
    return render(request, "accounts/user_login.html", {"next": next_url})




# =========================
# Browser–1: Register / Update Profile
# =========================
@login_required
def register_profile(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = UserRegisterForm(instance=request.user)

    return render(request, 'accounts/register_profile.html', {'form': form})

# =========================
# 🔐 Forgot Password
# =========================
def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            request.session['reset_email'] = form.cleaned_data['email']
            return redirect('reset_password')
    else:
        form = ForgotPasswordForm()

    return render(request, 'accounts/forgot_password.html', {'form': form})

# =========================
# 🔁 Reset Password
# =========================
def reset_password(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('forgot_password')

    user = User.objects.get(email=email)

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['password'])
            user.save()
            del request.session['reset_email']
            return redirect('login')
    else:
        form = ResetPasswordForm()

    return render(request, 'accounts/reset_password.html', {'form': form})



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import LoanVerification

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

