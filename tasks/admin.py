from django.contrib import admin
from .models import (
    User,
    LoanApplication,
    OTPVerification,
    InterestRate
)

# =============================
# Admin Actions
# =============================
@admin.action(description="Approve Selected Loans")
def approve_loans(modeladmin, request, queryset):
    queryset.update(status='Approved')


# =============================
# Interest Rate Admin
# =============================
@admin.register(InterestRate)
class InterestRateAdmin(admin.ModelAdmin):
    list_display = ('rate', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('rate',)


# =============================
# LoanApplication Admin (ONLY ONE)
# =============================
@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'amount',
        'total_paid',
        'total_payable',
        'status',
        'payment_status',
        'created_at',
    )

    list_filter = ('payment_status', 'created_at')
    search_fields = ('id',)
    readonly_fields = ('interest_rate',)
    actions = [approve_loans]


# =============================
# Other Models
# =============================
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'is_active')
    search_fields = ('username', 'email')


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp', 'is_verified', 'created_at')
    list_filter = ('is_verified',)




# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .models import LoanApplication

def is_admin(user):
    return user.is_authenticated and user.is_superuser


@user_passes_test(lambda u: u.is_superuser, login_url='no-permission')
def all_loans(request):

    if request.method == 'POST':
        loan_id = request.POST.get('loan_id')
        status = request.POST.get('status')

        loan = get_object_or_404(LoanApplication, id=loan_id)

        # 🔒 Fully paid হলে status change করা যাবে না
        if loan.display_status != 'Cleared':
            loan.status = status
            loan.save()

        return redirect('all_loan')

    loans = LoanApplication.objects.select_related('user').all().order_by('-id')
    return render(request, 'admin/all_loans.html', {'loans': loans})