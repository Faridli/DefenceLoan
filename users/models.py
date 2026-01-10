from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator

class LoanVerification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    bank_name = models.CharField(max_length=200, default="N/A")
    account_name = models.CharField(max_length=200)
    account_number = models.CharField(max_length=50)
    routing_number = models.CharField(max_length=50)
    declaration_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    submitted = models.BooleanField(default=False)  # <-- ফ্ল্যাগ
    def __str__(self):
        return f"{self.user.username} - Verification"
