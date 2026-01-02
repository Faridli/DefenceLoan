
# -------------------------------
# Mixin
# -------------------------------
class StyleFormMixin:
    base_classes = "border-blue-500 focus:ring-2 focus:ring-blue-300 rounded-md py-1 px-2"

    default_classes = {
        "input": f"form-input {base_classes}",
        "select": f"form-select {base_classes}",
        "checkbox": "form-checkbox h-5 w-5 text-blue-500",
    }

# -------------------------------
# 🔹 ForceMember Form
# -------------------------------
class ForceModelForm(forms.ModelForm,StyleFormMixin):
    svc_join = forms.CharField(
        label='Svc Join',
        required=False,
        widget=forms.TextInput(attrs={'class': default_classes, 'placeholder': 'DD/MM/YYYY'}),
        initial=date(current_year, 1, 1).strftime("%d/%m/%Y")
    )
    rab_join = forms.CharField(
        label='RAB Join',
        required=False,
        widget=forms.TextInput(attrs={'class': select, 'placeholder': 'DD/MM/YYYY'}),
        initial=date(current_year, 1, 1).strftime("%d/%m/%Y")
    )
    birth_day = forms.CharField(
        label='Birth Day',
        required=False,
        widget=forms.TextInput(attrs={'class': checkbox, 'placeholder': 'DD/MM/YYYY'}),
        initial=date(current_year, 1, 1).strftime("%d/%m/%Y")
    )

    class Meta:
        model = ForceMember
        exclude = ['company']
        fields = [
            'no', 'name', 'rank', 'force', 
            'svc_join','mother_unit', 'rab_join', 'birth_day',
            'nid', 'email', 'phone','photo', 'wf_phone','company',
        ]
        labels = {
            'no': 'Personal No',
            'name': 'Full Name',
            'rank': 'Rank',
            'force': 'Force',
            'mother_unit': 'moteher_unit',
            'svc_join': 'Svc Join',
            'rab_join': 'RAB Join',
            'birth_day': 'Birth Day',
            'nid': 'NID',
            'email': 'Email',
            'phone': 'Phone',
            'photo':'photo',
            'wf_phone': 'Wife Phone', 
            'company':'company',
        }
        widgets = {
            'no': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Personal Number'}),
            'name': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Full Name'}),
            'rank': forms.Select(attrs={'class': SELECT_CLASSES}),
            'force': forms.Select(attrs={'class': SELECT_CLASSES}),
            'mother_unit': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Unit Name....'}),
            'company': forms.Select(attrs={'class': SELECT_CLASSES}),
            'nid': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'NID'}),
            'email': forms.EmailInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Phone Number'}),
           'photo': forms.FileInput(attrs={'class': INPUT_CLASSES,}),
            'wf_phone': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Wife Phone Number'}),
        }

    # -------------------------------
    # Custom clean methods for DD/MM/YYYY
    # -------------------------------
    def clean_svc_join(self):
        data = self.cleaned_data['svc_join']
        if data:
            try:
                return datetime.strptime(data, "%d/%m/%Y").date()
            except ValueError:
                raise forms.ValidationError("Invalid date format. Use DD/MM/YYYY.")
        return None

    def clean_rab_join(self):
        data = self.cleaned_data['rab_join']
        if data:
            try:
                return datetime.strptime(data, "%d/%m/%Y").date()
            except ValueError:
                raise forms.ValidationError("Invalid date format. Use DD/MM/YYYY.")
        return None

    def clean_birth_day(self):
        data = self.cleaned_data['birth_day']
        if data:
            try:
                return datetime.strptime(data, "%d/%m/%Y").date()
            except ValueError:
                raise forms.ValidationError("Invalid date format. Use DD/MM/YYYY.")
        return None 
    


   tasks.views 

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count,Max, Min
from .models import ForceMember, Duty, MiRoomVisit,Ro 
from django.http import HttpResponseForbidden
from .forms import (
    ForceModelForm,
    CompanySelectForm,
    PresentModelForm,
    PermanentModelForm,
    DutyForm,
    MiRoomVisitForm,
    RoForm,
   
) 
from django.contrib.auth.decorators import user_passes_test 

def is_co(user):
    return user.groups.filter(name='Co').exists() 
def is_Admin(user):
    return user.groups.filter(name='Admin').exists() 

def is_employee(user):
    return user.groups.filter(name='employee').exists()
def is_mi(user):
    return user.groups.filter(name='mi').exists()
def is_ro(user):
    return user.groups.filter(name='ro').exists()
def is_Bn_HQ(user):
    return user.groups.filter(name='Bn HQ').exists()

# ---------------------------------------------------
# Dashboard
# ---------------------------------------------------
@user_passes_test(is_co, login_url='no-permission')
def Dashboard(request):
    return render(request, 'dashboard/dashboard.html')


# ---------------------------------------------------
# Bn HQ
# --------------------------------------------------- 
@user_passes_test(is_Bn_HQ, login_url='no-permission')
def Bn_Hq_Br(request):
    return render(request, 'bnhq/list.html')


# ---------------------------------------------------
# Force Bio Data Entry
# ---------------------------------------------------
@user_passes_test(is_employee, login_url='no-permission')
def Force_bio(request):
    if request.method == 'POST':
        force_form = ForceModelForm(request.POST)
        present_form = PresentModelForm(request.POST)
        permanent_form = PermanentModelForm(request.POST)

        if force_form.is_valid() and present_form.is_valid() and permanent_form.is_valid():
            force = force_form.save()

            present = present_form.save(commit=False)
            present.member = force
            present.save()

            permanent = permanent_form.save(commit=False)
            permanent.member = force
            permanent.save()

            messages.success(request, "saved successfully!")
            return redirect('force-bio')
        else:
            messages.error(request, "Please fix the errors!")
            print("ForceForm errors:", force_form.errors)
            print("PresentForm errors:", present_form.errors)
            print("PermanentForm errors:", permanent_form.errors)

    else:
        force_form = ForceModelForm()
        present_form = PresentModelForm()
        permanent_form = PermanentModelForm()

    context = {
        'force_form': force_form,
        'present_form': present_form,
        'permanent_form': permanent_form,
    }
    return render(request, 'dashboard/bio.html', context)


# ---------------------------------------------------
# Force Detail / Company Select
# ---------------------------------------------------
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from .models import ForceMember
from .forms import CompanySelectForm
@user_passes_test(is_Bn_HQ, login_url='no-permission')
def Force_detail(request):

    # 🔹 Main list (OUT বাদ)
    members = ForceMember.objects.exclude(company__iexact="RAB-1 Out")\
        .select_related('present_address', 'permanent_address')

    # 🔹 OUT list
    out_members = ForceMember.objects.filter(company__iexact="RAB-1 Out").order_by('-out_date')

    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        member_id = request.POST.get("member_id")
        member = get_object_or_404(ForceMember, id=member_id)

        form = CompanySelectForm(request.POST, instance=member)
        if form.is_valid():
            company = form.cleaned_data["company"].strip()
            member.company = company

            # 🔴 OUT হলে date set
            if company.lower() == "rab-1 out":
                if not member.out_date:
                    member.out_date = timezone.now().date()
            else:
                member.out_date = None

            member.save()

            return JsonResponse({
                "success": True,
                "company_name": member.get_company_display(),
                "is_out": company.lower() == "rab-1 out",
                "out_date": member.out_date.strftime("%d-%m-%Y") if member.out_date else ""
            })

        return JsonResponse({"success": False})

    # 🔹 Forms dictionary for each member
    forms_dict = {m.id: CompanySelectForm(instance=m) for m in members}

    return render(request, "bnhq/force_detail.html", {
        "members": members,
        "out_members": out_members,
        "forms_dict": forms_dict
    })

#--------------------------------------------------
# Company Wise..............................
# --------------------------------------------------- 
@user_passes_test(is_Bn_HQ, login_url='no-permission')
def Company_members_of_bnhq(request):
    members = ForceMember.objects.filter(company='Bn HQ').order_by('rank') 
    force_state = members.values('force').annotate(total=Count('id'))
    rank_state = members.values('rank').annotate(total=Count('id'))

    context = {
            'members':members,
            'company': 'Bn HQ', 
            'force_state': force_state,
            'rank_state': rank_state
    }

    return render(request, 'bnhq/company_members.html',context)
# ---------------------------------------------------
# Address View
# ---------------------------------------------------
@user_passes_test(is_co, login_url='no-permission')
def Address(request, member_id):
    m = get_object_or_404(ForceMember, id=member_id)
    context = {
        "m": m,
        "present_dict": {
            "House": m.present_address.house,
            "Road": m.present_address.road,
            "Sector": m.present_address.sector,
            "Village": m.present_address.village,
            "Post": m.present_address.post,
            "District": m.present_address.district,
        },
        "permanent_dict": {
            "House": m.permanent_address.house,
            "Road": m.permanent_address.road,
            "Sector": m.permanent_address.sector,
            "Village": m.permanent_address.village,
            "Post": m.permanent_address.post,
            "District": m.permanent_address.district,
        },
        "service_dict": {
            "Svc Join": m.svc_join,
            "RAB Join": m.rab_join,
            "Mother_unit": m.mother_unit,
            "NID": m.nid,
            "Birth Day": m.birth_day,
            "WF Phone": m.wf_phone,
        },
    }
    return render(request, "bnhq/address.html", context)


# ---------------------------------------------------
# Duty Views
# ---------------------------------------------------
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden

def duty_create_group(request, company):
    # 1️⃣ Login check
    if not request.user.is_authenticated:
        return redirect('login')

    # 2️⃣ Company-wise permission check
    if not request.user.groups.filter(name=company).exists():
        return HttpResponseForbidden("No permission for this company")

    # 3️⃣ Handle POST
    if request.method == "POST":
        form = DutyForm(request.POST, request.FILES)
        if form.is_valid():
            raw_numbers = form.cleaned_data['member_numbers']
            numbers = [n.strip() for n in raw_numbers.replace(",", " ").split() if n.strip()]

            valid_members, invalid_numbers = [], []

            for num in numbers:
                member = ForceMember.objects.filter(no=num, company=company).first()
                if member:
                    valid_members.append(member)
                else:
                    invalid_numbers.append(num)

            if invalid_numbers:
                messages.error(
                    request, 
                    f"Invalid Member Numbers: {', '.join(invalid_numbers)}"
                )
                return render(request, 'bnhq/duty_create_group.html', {
                    'form': form,
                    'company': company
                })

            # 4️⃣ Create Duty objects
            Duty.objects.bulk_create([
                Duty(
                    member=member,
                    name=member.name,
                    rank=member.get_rank_display(),
                    phone=member.phone,
                    date=form.cleaned_data['date'],
                    start_time=form.cleaned_data['start_time'],
                    end_time=form.cleaned_data['end_time'],
                    destination=form.cleaned_data['destination'],
                ) for member in valid_members
            ])

            messages.success(request, f"{company} group duty created successfully!")
            return redirect('duty_list', company=company)  # Redirect with company param

    else:
        form = DutyForm()

    return render(request, 'bnhq/duty_create_group.html', {
        'form': form,
        'company': company
    })


@user_passes_test(is_Admin, login_url='no-permission')
def duty_edit(request, pk):
    duty = get_object_or_404(Duty, pk=pk)
    form = DutyForm(request.POST or None, instance=duty)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('duty_list')
    return render(request, 'bnhq/duty_form.html', {'form': form, 'edit': True})


def duty_list_by_company(request, company):

    # 1️⃣ login check
    if not request.user.is_authenticated:
        return redirect('login')

    # 2️⃣ company-wise permission check
    if not request.user.groups.filter(name=company).exists():
        return HttpResponseForbidden("no permission")

    # 3️⃣ data query (permission pass হলে)
    duties = Duty.objects.filter(
        member__company=company
    ).order_by('destination', 'date')

    return render(request, 'bnhq/duty_list.html', {
        'duties': duties,
        'company': company
    })


    duties = Duty.objects.filter(member__company=company).order_by('destination', 'date') 
    # login check
    if not request.user.is_authenticated:
        return redirect('login')

    # company-wise permission check
    if not request.user.groups.filter(name=company).exists():
        return HttpResponseForbidden("no permission")
    return render(request, 'bnhq/duty_list.html', {'duties': duties, 'company': company})


    duties = Duty.objects.filter(member__company=company).order_by('destination', 'date') 
    
    return render(request, 'bnhq/duty_list.html', {'duties': duties, 'company': company})

@user_passes_test(is_Admin, login_url='no-permission')
def duty_delete(request, pk):
    duty = get_object_or_404(Duty, pk=pk)
    if request.method == "POST":
        duty.delete()
        return redirect('duty_list')
    return render(request, 'bnhq/duty_delete.html', {'duty': duty})


# ---------------------------------------------------
# MI Room Views
# --------------------------------------------------- 
@user_passes_test(is_mi, login_url='no-permission')
def miroom_daily_report(request):
    visits = MiRoomVisit.objects.select_related("member").order_by("-date", "member__rank")
    grouped_data = {}

    for v in visits:
        date = v.date
        if date not in grouped_data:
            grouped_data[date] = {"count": 0, "items": []}
        grouped_data[date]["count"] += 1
        grouped_data[date]["items"].append(v)

    return render(request, 'mi/miroom.html', {"grouped_data": grouped_data}) 

@user_passes_test(is_mi, login_url='no-permission')
def miroom_visit_create(request):
    member = None
    if request.method == "POST":
        form = MiRoomVisitForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "MI Room Visit saved successfully!")
            return redirect('miroom_visit_list')
        else:
            # যদি Per Number মিল না হয়
            per_no = request.POST.get('per_number')
            if per_no:
                member = ForceMember.objects.filter(no=per_no).first()
    else:
        form = MiRoomVisitForm()
    return render(request, 'mi/miroom_create.html', {'form': form, 'member': member})

def get_member(request, per_no):
    try:
        member = ForceMember.objects.get(no=per_no)
        return JsonResponse({
            "success": True,
            "id": member.id,
            "name": member.name,
            "rank": member.get_rank_display()
        })
    except ForceMember.DoesNotExist:
        return JsonResponse({"success": False})



# -----------------------------
# Ro Create
# -----------------------------
@user_passes_test(is_ro, login_url='no-permission')
def ro_create(request):
    form = RoForm()
    member = None
    if request.method == "POST":
        form = RoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('ro-list')  # redirect করুন যেখানে চান 
    else:
        print(form.errors)
    return render(request, 'ro/ro_form.html', {'form': form, 'member': member}) 

@user_passes_test(is_ro, login_url='no-permission')
def ro_list(request):
    ro_entries = Ro.objects.all().order_by()
    return render(request, 'ro/ro_list.html', {'ro_entries': ro_entries})



def member_get(request, query):
    try:
        # প্রথমে per_number দিয়ে খুঁজবে, যদি না পাওয়া যায় তাহলে nid দিয়ে খুঁজবে
        member = ForceMember.objects.filter(no=query).first()
        if not member:
            member = ForceMember.objects.filter(nid=query).first()

        if member:
            return JsonResponse({
                "success": True,
                "rank": member.rank,
                "name": member.name
            })
        else:
            return JsonResponse({"success": False})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

# def Acct_Br(request):


# ---------------------------------------------------
# CPC 
# ---------------------------------------------------
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden

def CPC_One_Br(request, company):
    # login check
    if not request.user.is_authenticated:
        return redirect('login')

    # company-wise permission check
    if not request.user.groups.filter(name=company).exists():
        return HttpResponseForbidden("no permission")

    return render(request, 'cpcone/list.html', {
        'company': company
    })







pip install -r requirements.txt; python manage.py collectstatic --noinput   # টাকা দিয়ে মাই্রগ্রেশন করতে হয় 
pip install -r requirements.txt && python manage.py migrate   # টাকা ছাড়া মাই্রগ্রেশন করতে হয় 
