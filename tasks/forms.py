from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserVerification

class UserRegisterForm(UserCreationForm):
    
    class Meta:
        model = User
        fields = ['username','email','password1','password2']


from django.core.exceptions import ValidationError
from .models import User


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            'service_id_number',
            'rank',
            'name',
            'phone',
            'corps',
            'joining_date',
            'birth_date',
            'national_id_number',
            # 'service_id_card',

            # 'service_id_card',
            # 'live_photo',

            'spouse_name',
            'spouse_nid',
            'spouse_birth_date',
            # 'spouse_national_id_card',
        ]

        widgets = {
            'service_id_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border-2 border-blue-200 rounded-lg',
                'placeholder': 'Service ID Number'
            }),
            'rank': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border-2 border-blue-200 rounded-lg',
                'placeholder': 'Rank'
            }),
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border-2 border-blue-200 rounded-lg',
                'placeholder': 'Full Name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border-2 border-blue-200 rounded-lg',
                'placeholder': '11 digit Phone Number'
            }),
            'corps': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border-2 border-blue-200 rounded-lg',
                
            }),
            'joining_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border-2 border-blue-200 rounded-lg'
            }),
            'birth_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border-2 border-blue-200 rounded-lg'
            }),
            'national_id_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border-2 border-blue-200 rounded-lg',
                'placeholder': '10 or 17 digit NID'
            }),
            'spouse_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border-2 border-blue-200 rounded-lg',
                'placeholder': 'Full Name'
            }),
            'spouse_nid': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border-2 border-blue-200 rounded-lg',
                'placeholder': 'Spouse NID (10 or 17 digits)'
            }),
            'spouse_birth_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border-2 border-blue-200 rounded-lg'
            }),
        }

    # =========================
    # Extra Validation (Optional but Recommended)
    # =========================
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.isdigit():
            raise ValidationError("Phone number must contain only digits.")
        return phone

    def clean_national_id_number(self):
        nid = self.cleaned_data.get('national_id_number')
        if nid and len(nid) not in [10, 17]:
            raise ValidationError("National ID must be exactly 10 or 17 digits.")
        return nid



class UserKycForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            
            'service_id_card',
            'national_id_card',
            'live_photo',      
            'spouse_national_id_card',
        ]

            
