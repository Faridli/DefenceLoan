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
    national_id_back = models.FileField(
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
    spouse_nid_back = models.FileField(
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

# =========================
# InterestRate
# =========================
class InterestRate(models.Model):
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.is_active:
            InterestRate.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.rate}% {'(Active)' if self.is_active else ''}"


from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class LoanApplication(models.Model):
    comment = models.TextField(blank=True, null=True)

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Cleared', 'Cleared'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
    )

    # ----------------------------
    # Basic Info
    # ----------------------------
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    duration_months = models.PositiveIntegerField(default=12)
    purpose = models.TextField()

    # ----------------------------
    # Salary / Bank Info
    # ----------------------------
    basic_salary = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    account_name = models.CharField(max_length=100, null=True, blank=True)
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    salary_account_number = models.CharField(max_length=50, null=True, blank=True)
    previous_loans = models.TextField(null=True, blank=True)
    salary_certificate = models.ImageField(
        upload_to='salary_certificates/', null=True, blank=True
    )

    # ----------------------------
    # Interest & Calculation
    # ----------------------------
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Locked interest rate at loan creation"
    )

    monthly_installment = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    total_payable = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    total_interest = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )

    total_paid = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )

    # ----------------------------
    # Status & Payment
    # ----------------------------
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='Pending'
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='PENDING'
    )

    tran_id = models.CharField(
        max_length=100, blank=True, null=True, unique=True
    )
    # ----------------------------
    # Payment Tracking
    # ----------------------------
    last_payment_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # ----------------------------
    # SAVE METHOD (RATE LOCK + CALC)
    # ----------------------------
    def save(self, *args, **kwargs):

        from .models import InterestRate  # circular import safe

        # 🔒 Lock interest rate on first save
        if not self.pk:
            active_rate = InterestRate.objects.filter(is_active=True).first()
            if not active_rate:
                raise ValidationError("No active interest rate set by admin.")
            self.interest_rate = active_rate.rate

        # 🔢 EMI Calculation
        if self.amount and self.duration_months:
            amount = Decimal(self.amount)
            rate = Decimal(self.interest_rate)
            months = int(self.duration_months)

            yearly_interest = (amount * rate) / Decimal("100")
            total_interest = (yearly_interest / Decimal("12")) * months

            self.total_interest = total_interest
            self.total_payable = amount + total_interest
            self.monthly_installment = self.total_payable / months

        super().save(*args, **kwargs)

    # ----------------------------
    # Properties
    # ----------------------------
    @property
    def remaining_amount(self):
        return max(
            (self.total_payable or Decimal("0.00"))
            - (self.total_paid or Decimal("0.00")),
            Decimal("0.00")
        )

    @property
    def months_paid(self):
        if not self.monthly_installment or self.monthly_installment == 0:
            return 0
    # Decimal দিয়ে safe division এবং integer conversion
        return int(self.total_paid // self.monthly_installment)


    @property
    def display_status(self):
        if self.total_payable and self.total_paid >= self.total_payable:
            return "Cleared"
        return self.status

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



# tasks/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date

User = get_user_model() 
class AutoDebit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField(default=timezone.now)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    months = models.PositiveIntegerField()
    next_payment_date = models.DateField()
    is_active = models.BooleanField(default=True)
    gateway_reference = models.CharField(max_length=255)
    next_payment_date = models.DateField(default=date.today)
