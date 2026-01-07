from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, ForgotPasswordForm, ResetPasswordForm
from tasks.models import User


from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import UserRegisterForm

def register_account(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)   # Auto login
            return redirect('profile')    
    else:
        form = UserRegisterForm()

    return render(request, 'accounts/register_account.html', {'form': form})

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
