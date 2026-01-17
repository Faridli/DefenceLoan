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






# from django.contrib import admin
# from .models import User, LoanApplication, OTPVerification

# # =============================
# # Loan Admin Actions
# # =============================
# @admin.action(description="Approve Selected Loans")
# def approve_loans(modeladmin, request, queryset):
#     queryset.update(status='Approved')



# from django.contrib import admin
# from .models import InterestRate, LoanApplication

# @admin.register(InterestRate)
# class InterestRateAdmin(admin.ModelAdmin):
#     list_display = ('rate', 'is_active', 'created_at')


# @admin.register(LoanApplication)
# class LoanApplicationAdmin(admin.ModelAdmin):
#     readonly_fields = ('interest_rate',)

# # =============================
# # LoanApplication Admin
# # =============================
# @admin.register(LoanApplication)
# class LoanAdmin(admin.ModelAdmin):
#     list_display = ('id', 'amount', 'total_paid', 'total_payable', 'status')  # status ok, readonly
#     # list_filter থেকে 'status' remove করুন
#     list_filter = ('payment_status', 'created_at')  # example


# # =============================
# # Other Models
# # =============================
# admin.site.register(User)
# admin.site.register(OTPVerification)
