from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

def validate_jpg(value):
    import os
    ext = os.path.splitext(value.name)[1]
    if ext.lower() not in ['.jpg', '.jpeg']:
        raise ValidationError('Only JPG/JPEG files are allowed.')

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator, FileExtensionValidator
from django.core.exceptions import ValidationError


# 🔹 JPG validation (live photo)
def validate_jpg(value):
    if not value.name.lower().endswith('.jpg'):
        raise ValidationError('Only JPG files are allowed.')


class User(AbstractUser):

    # =========================
    # Basic Information
    # =========================
    service_id_number = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    rank = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    joining_date = models.DateField(null=True, blank=True)
    CORPS_CHOICES = [
    ('Army', 'No Army'),
    ('Armored Corps', 'Armored Corps'),
    ('Artillery', 'Artillery'),
    ('Engineers', 'Engineers'),
    ('Signals', 'Signals'),
    ('Infantry', 'Infantry'),
    ('Army Service Corps', 'Army Service Corps'),
    ('Ordnance Corps', 'Ordnance Corps'),
    ('Electrical and Mechanical Engineering Corps', 'Electrical and Mechanical Engineering Corps'),
    ('Special Operations', 'Special Operations'),
    ('Aviation', 'Aviation'),
    ('Military Police', 'Military Police'),
    ('Army Dental Corps', 'Army Dental Corps'),
    ('Army Education Corps', 'Army Education Corps'),
    ('Army Corps of Clerks', 'Army Corps of Clerks'),
    ('Remounts, Veterinary and Farms Corps', 'Remounts, Veterinary and Farms Corps'),
    ('Army Nursing Corps', 'Army Nursing Corps'),
    ]

    corps = models.CharField(
    max_length=100,
    choices=CORPS_CHOICES,
    default='No Army'
    ) 


    phone = models.CharField(
        max_length=11,
        blank=True,
        null=True
    )

    birth_date = models.DateField(
        blank=True,
        null=True
    )

    # =========================
    # National ID (User)
    # =========================
    national_id_number = models.CharField(
        max_length=17,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^(\d{10}|\d{17})$',
                message='National ID must be exactly 10 or 17 digits'
            )
        ]
    )

    national_id_card = models.FileField(
        upload_to='nid/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'pdf'])]
    )

    # =========================
    # Service ID
    # =========================
    service_id_card = models.FileField(
        upload_to='service_id/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'pdf'])]
    )

    # =========================
    # Live Photo
    # =========================
    live_photo = models.FileField(
        upload_to='photos/',
        blank=True,
        null=True,
        validators=[validate_jpg]
    )

    # =========================
    # Spouse Information
    # =========================
    spouse_name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    spouse_nid = models.CharField(
        max_length=17,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^(\d{10}|\d{17})$',
                message='Spouse NID must be exactly 10 or 17 digits'
            )
        ]
    )

    spouse_birth_date = models.DateField(
        blank=True,
        null=True
    )

    spouse_national_id_card = models.FileField(
        upload_to='nid/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'pdf'])]
    )

    # =========================
    # String Representation
    # =========================
    def __str__(self):
        return self.username

from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator

# ===============================
# Loan Application staus of user
# ===============================
class LoanApplication(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    monthly_installment = models.PositiveIntegerField()
    purpose = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    bank_name = models.CharField(max_length=200, blank=True, null=True)
    salary_account_number = models.CharField(max_length=50, blank=True, null=True)
    previous_loans = models.JSONField(blank=True, null=True)
    salary_certificate = models.FileField(
        upload_to='kyc_docs/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'pdf'])],
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} BDT"



# =========================
# Loan Application Status of Admin
# =========================
class LoanAdmin(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} BDT" 




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
