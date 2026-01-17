import re
from django import forms
from django.contrib.auth.hashers import make_password
from tasks.models import User

# =========================
# Base CSS Classes
# =========================
base_classes = "w-full px-4 py-2 border-2 border-blue-300 rounded-lg focus:outline-none focus:ring"

# ==================================================
# 🔐 Forgot Password Form
# ==================================================
class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label="Registered Email",
        widget=forms.EmailInput(attrs={"class": base_classes})
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("No user found with this email.")
        return email

# ==================================================
# 🔁 Reset Password Form
# ==================================================
class ResetPasswordForm(forms.Form):
    password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={"class": base_classes})
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": base_classes})
    )

    def clean_password(self):
        password = self.cleaned_data.get('password')
        errors = []

        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', password):
            errors.append("Must include one uppercase letter.")
        if not re.search(r'[a-z]', password):
            errors.append("Must include one lowercase letter.")
        if not re.search(r'[0-9]', password):
            errors.append("Must include one number.")
        if not re.search(r'[@#$^&!\-+=]', password):
            errors.append("Must include one special character.")

        if errors:
            raise forms.ValidationError(errors)

        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

# ==================================================
# 👤 User Registration / Profile Form
# ==================================================
class UserRegisterForm(forms.ModelForm):
    # 🔹 Account Info
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={"class": base_classes})
    )
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={"class": base_classes})
    ) 
    phone = forms.CharField(
    label="Phone Number",
    max_length=11,
    widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2 border-2 border-blue-200 rounded-lg',
        'placeholder': '01XXXXXXXXX'
    })
)

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": base_classes}),
        required=False  # profile update may not require password
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": base_classes}),
        required=False
    )

    class Meta:
        model = User
        fields = ['username','phone','email']

    # =========================
    # Validations
    # =========================
    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            return password  # skip if empty during profile update

        errors = []

        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', password):
            errors.append("Must include one uppercase letter.")
        if not re.search(r'[a-z]', password):
            errors.append("Must include one lowercase letter.")
        if not re.search(r'[0-9]', password):
            errors.append("Must include one number.")
        if not re.search(r'[@#$^&!\-+=]', password):
            errors.append("Must include one special character.")

        if errors:
            raise forms.ValidationError(errors)

        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

    # =========================
    # Save (Hash Password)
    # =========================
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.password = make_password(password)
        if commit:
            user.save()
        return user 
    


from django import forms
base_classes = "w-full border-2 border-blue-200 p-2 rounded"
class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': base_classes,
            'placeholder': 'Enter your registered email'
        })
    )

base_classes = "w-full border p-2 rounded"
class ResetPasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': base_classes,
            'placeholder': 'New Password'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full border p-2 rounded',
            'placeholder': 'Confirm New Password'
        })
    )


from tasks.models import LoanApplication

class LoanApplyForm(forms.ModelForm):
    class Meta:
        model = LoanApplication
        fields = ['amount', 'duration_months', 'purpose']
        # interest_rate form এ থাকবে না, সিস্টেম auto fill করবে



# class AssignRoleForm(forms.Form):
#     role = forms.ModelChoiceField(
#         queryset=Group.objects.all(),
#         empty_label="Select Role"
#     ) 


# class CreateGroupForm(forms.ModelForm):
#     permissions = forms.ModelMultipleChoiceField(
#         queryset=Permission.objects.all(),
#         widget=forms.CheckboxSelectMultiple(),
#         required=False,
#         label='Assign Permission'
#     )

#     class Meta:
#         model = Group
#         fields = ['name', 'permissions']




