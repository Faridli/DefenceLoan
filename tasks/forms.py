from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserVerification

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=True)
    birth_date = forms.DateField(required=True, widget=forms.DateInput(attrs={'type':'date'}))
    spouse_name = forms.CharField(required=False)
    spouse_nid = forms.CharField(required=False)
    national_id = forms.FileField(required=True)
    service_id_card = forms.FileField(required=True)
    live_photo = forms.ImageField(required=True)

    class Meta:
        model = User
        fields = ['username','email','phone','password1','password2','birth_date','spouse_name','spouse_nid','national_id','service_id_card','live_photo']
