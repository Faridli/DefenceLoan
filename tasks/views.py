from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from tasks.models import ForceMember
from tasks.forms import ForceModelForm,CompanySelectForm, PresentModelForm, PermanentModelForm
from django.db.models import Count, Prefetch, Q


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

        # Form validation
        if force_form.is_valid() and present_form.is_valid() and permanent_form.is_valid():
            # Save ForceMember
            force = force_form.save()
            # force.company.add(Company.objects.get(id=1))

            # Save PresentAddress
            present = present_form.save(commit=False)
            present.member = force
            present.save()

            # Save PermanentAddress
            permanent = permanent_form.save(commit=False)
            permanent.member = force
            permanent.save()

            # Success message
            messages.success(request, "saved successfully!")
            return redirect('force-bio')

        else:
            # Debug: print form errors to console
            messages.error(request, "Please fix the errors!")
            print("errors:", force_form.errors)
            print("errors:", present_form.errors)
            print("errors:", permanent_form.errors)

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
# 
# ---------------------------------------------------
# views.py
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

def Force_detail(request):
    members = ForceMember.objects.all().select_related(
        'present_address', 'permanent_address'
    )

    # Handle AJAX POST
    if request.method == "POST":
        member_id = request.POST.get("member_id")
        member = get_object_or_404(ForceMember, id=member_id)

        form = CompanySelectForm(request.POST, instance=member)

        if form.is_valid():
            form.save()

            # AJAX request → return JSON
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({
                    "success": True,
                    "company_name": member.company  # updated value
                })

            return redirect("force-detail")

        else:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"success": False})

    # For GET request → load table
    forms_dict = {m.id: CompanySelectForm(instance=m) for m in members}

    return render(request, "bnhq/force_detail.html", {
        "members": members,
        "forms_dict": forms_dict,
    })


#.......................
# Address................
# ....................... 

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
            "Mother_unit":m.mother_unit,
            "NID": m.nid,
            "Birth Day": m.birth_day,
            "WF Phone": m.wf_phone,
        },
    }
    return render(request, "bnhq/address.html", context)


from django.shortcuts import render, redirect
from .forms import DutyForm
from .models import ForceMember
# def duty_create(request):
#     if request.method == "POST":
#         form = DutyForm(request.POST)
#         if form.is_valid():
#             member_no = form.cleaned_data['member_no']
#             member = ForceMember.objects.filter(no=member_no).first()

#             if not member:
#                 form.add_error('member_no', "Member not found")
#             else:
#                 duty = form.save(commit=False)
#                 duty.member = member
#                 duty.save()
#                 return redirect('duty_list')
#     else:
#         form = DutyForm()

#     members = ForceMember.objects.all()   # ★ ForceMember list send

#     return render(request, 'bnhq/duty_form.html', {
#         'form': form,
#         'members': members
#     })



# views.py
from django.shortcuts import render, redirect
from .forms import DutyForm
from .models import Duty

def duty_create_group(request):
    if request.method == "POST":
        form = DutyForm(request.POST)
        if form.is_valid():
            members = form.cleaned_data['members']
            destination = form.cleaned_data['destination']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']

            for member in members:
                duty = Duty(
                    member=member,
                    name=member.name,
                    rank=member.get_rank_display(),
                    phone=member.phone,
                    destination=destination,
                    start_time=start_time,
                    end_time=end_time
                )
                duty.save()

            return redirect('duty_list')
    else:
        form = DutyForm()
    return render(request, 'bnhq/duty_create_group.html', {'form': form})



from django.shortcuts import render, get_object_or_404, redirect
from .models import Duty
from .forms import DutyForm

def duty_edit(request, pk):
    duty = get_object_or_404(Duty, pk=pk)
    if request.method == "POST":
        form = DutyForm(request.POST, instance=duty)
        if form.is_valid():
            form.save()
            return redirect('duty_list')
    else:
        form = DutyForm(instance=duty)
    return render(request, 'bnhq/duty_form.html', {'form': form, 'edit': True})


from .models import Duty
def duty_list(request):
    duties = Duty.objects.all().order_by('-date', '-start_time')
    return render(request, 'bnhq/duty_list.html', {'duties': duties})


# views.py
def duty_delete(request, pk):
    duty = get_object_or_404(Duty, pk=pk)
    if request.method == "POST":
        duty.delete()
        return redirect('duty_list')
    return render(request, 'bnhq/duty_delete.html', {'duty': duty})
