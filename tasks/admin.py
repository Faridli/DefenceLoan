from django.contrib import admin
from .models import User, LoanApplication, OTPVerification

# =============================
# Loan Admin Actions
# =============================
@admin.action(description="Approve Selected Loans")
def approve_loans(modeladmin, request, queryset):
    queryset.update(status='Approved')

# =============================
# LoanApplication Admin
# =============================
@admin.register(LoanApplication)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'monthly_installment', 'status', 'created_at')  # মডেলের ফিল্ড নাম ঠিক
    list_filter = ('status',)
    search_fields = ('user__username', 'amount', 'bank_name')
    actions = [approve_loans]

# =============================
# Other Models
# =============================
admin.site.register(User)
admin.site.register(OTPVerification)
