from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count
from .models import ForceMember, Duty, MiRoomVisit
from .forms import (
    ForceModelForm,
    CompanySelectForm,
    PresentModelForm,
    PermanentModelForm,
    DutyForm,
    MiRoomVisitForm
)

# ---------------------------------------------------
# Dashboard
# ---------------------------------------------------
def Dashboard(request):
    return render(request, 'dashboard/dashboard.html')


# ---------------------------------------------------
# Bn HQ
# ---------------------------------------------------
def Br(request):
    return render(request, 'bnhq/list.html')


# ---------------------------------------------------
# Force Bio Data Entry
# ---------------------------------------------------
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
def Force_detail(request):
    members = ForceMember.objects.all().select_related('present_address', 'permanent_address')

    if request.method == "POST":
        member_id = request.POST.get("member_id")
        member = get_object_or_404(ForceMember, id=member_id)
        form = CompanySelectForm(request.POST, instance=member)

        if form.is_valid():
            form.save()
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"success": True, "company_name": member.company})
            return redirect("force-detail")
        else:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"success": False})

    forms_dict = {m.id: CompanySelectForm(instance=m) for m in members}
    return render(request, "bnhq/force_detail.html", {"members": members, "forms_dict": forms_dict})


# ---------------------------------------------------
# Address View
# ---------------------------------------------------
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
def duty_create_group(request):
    if request.method == "POST":
        form = DutyForm(request.POST)
        if form.is_valid():
            raw_numbers = form.cleaned_data['member_numbers']
            numbers = [n.strip() for n in raw_numbers.replace(",", " ").split() if n.strip()]

            valid_members, invalid_numbers = [], []

            for num in numbers:
                member = ForceMember.objects.filter(no=num).first()
                if member:
                    valid_members.append(member)
                else:
                    invalid_numbers.append(num)

            if invalid_numbers:
                messages.error(request, f"Invalid Member Numbers: {', '.join(invalid_numbers)}")
                return render(request, 'bnhq/duty_create_group.html', {'form': form})

            for member in valid_members:
                Duty.objects.create(
                    member=member,
                    name=member.name,
                    rank=member.get_rank_display(),
                    phone=member.phone,
                    date=form.cleaned_data['date'],
                    start_time=form.cleaned_data['start_time'],
                    end_time=form.cleaned_data['end_time'],
                    destination=form.cleaned_data['destination'],
                )

            messages.success(request, "Group duty created successfully!")
            return redirect('duty_list')
    else:
        form = DutyForm()

    return render(request, 'bnhq/duty_create_group.html', {'form': form})


def duty_edit(request, pk):
    duty = get_object_or_404(Duty, pk=pk)
    form = DutyForm(request.POST or None, instance=duty)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('duty_list')
    return render(request, 'bnhq/duty_form.html', {'form': form, 'edit': True})


def duty_list(request):
    duties = Duty.objects.all().order_by('-date', '-start_time')
    return render(request, 'bnhq/duty_list.html', {'duties': duties})


def duty_delete(request, pk):
    duty = get_object_or_404(Duty, pk=pk)
    if request.method == "POST":
        duty.delete()
        return redirect('duty_list')
    return render(request, 'bnhq/duty_delete.html', {'duty': duty})


# ---------------------------------------------------
# MI Room Views
# ---------------------------------------------------
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
