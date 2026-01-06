from django.contrib import admin
from .models import User, LoanApplication, OTPVerification

@admin.action(description="Approve Selected Loans")
def approve_loans(modeladmin, request, queryset):
    queryset.update(status='Approved')

@admin.register(LoanApplication)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'months', 'status')
    list_filter = ('status',)
    actions = [approve_loans]

admin.site.register(User)
admin.site.register(OTPVerification)
