from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

def validate_jpg(value):
    import os
    ext = os.path.splitext(value.name)[1]
    if ext.lower() not in ['.jpg', '.jpeg']:
        raise ValidationError('Only JPG/JPEG files are allowed.')

class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    national_id = models.FileField(upload_to='nid/', blank=True, null=True)
    service_id_card = models.FileField(upload_to='service_id/', blank=True, null=True)
    live_photo = models.FileField(upload_to='photos/', blank=True, null=True, validators=[validate_jpg])
    birth_date = models.DateField(blank=True, null=True)
    spouse_name = models.CharField(max_length=255, blank=True, null=True)
    spouse_nid = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.username

class LoanApplication(models.Model):
    STATUS_CHOICES = (('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected'))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    months = models.PositiveIntegerField()
    purpose = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_account_number = models.CharField(max_length=50, blank=True, null=True)
    previous_loans = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class OTPVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    purpose = models.CharField(max_length=50)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

class Payment(models.Model):
    loan = models.ForeignKey(LoanApplication, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

class UserDevice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    device_info = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class UserVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nid_image = models.ImageField(upload_to='nid/')
    service_id_image = models.ImageField(upload_to='service/')
    live_photo = models.ImageField(upload_to='live/', validators=[validate_jpg])
    is_verified = models.BooleanField(default=False)


from django.conf import settings
from django.db import models

class SomeModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
