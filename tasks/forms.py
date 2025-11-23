from django import forms
from datetime import date, datetime
from .models import ForceMember, PresentAddress, PermanentAddress

current_year = date.today().year

# -------------------------------
# CSS Classes
# -------------------------------
INPUT_CLASSES = "form-input border-blue-500 focus:ring-2 focus:ring-blue-300 rounded-md py-1 px-2"
SELECT_CLASSES = "form-select border-blue-500 focus:ring-2 focus:ring-blue-300 rounded-md py-1 px-2"
CHECKBOX_CLASSES = "form-checkbox h-5 w-5 text-blue-500"

# -------------------------------
# 🔹 ForceMember Form
# -------------------------------
class ForceModelForm(forms.ModelForm):
    svc_join = forms.CharField(
        label='Svc Join',
        required=False,
        widget=forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'DD/MM/YYYY'}),
        initial=date(current_year, 1, 1).strftime("%d/%m/%Y")
    )
    rab_join = forms.CharField(
        label='RAB Join',
        required=False,
        widget=forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'DD/MM/YYYY'}),
        initial=date(current_year, 1, 1).strftime("%d/%m/%Y")
    )
    birth_day = forms.CharField(
        label='Birth Day',
        required=False,
        widget=forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'DD/MM/YYYY'}),
        initial=date(current_year, 1, 1).strftime("%d/%m/%Y")
    )

    class Meta:
        model = ForceMember
        exclude = ['company']
        fields = [
            'no', 'name', 'rank', 'force', 
            'svc_join','mother_unit', 'rab_join', 'birth_day',
            'nid', 'email', 'phone', 'wf_phone','company',
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

# -------------------------------
# 🔹 Present Address Form
# -------------------------------
class PresentModelForm(forms.ModelForm):
    class Meta:
        model = PresentAddress
        fields = ['house', 'road', 'sector', 'village','post', 'thana', 'district', 'division']
        labels = {
            'house': 'House No',
            'road': 'Road No',
            'sector': 'Sector',
            'village': 'Village',
            'post':'post',
            'thana': 'Police Station',
            'district': 'District',
            'division': 'Division',
        }
        widgets = {f: forms.TextInput(attrs={'class': INPUT_CLASSES}) for f in fields}

# -------------------------------
# 🔹 Permanent Address Form
# -------------------------------
class PermanentModelForm(forms.ModelForm):
    same_as_present = forms.BooleanField(
        required=False,
        label='Same as Present Address',
        widget=forms.CheckboxInput(attrs={'class': CHECKBOX_CLASSES})
    )

    class Meta:
        model = PermanentAddress
        fields = ['house', 'road', 'sector', 'village','post', 'thana', 'district', 'division']
        labels = {
            'house': 'House No',
            'road': 'Road No',
            'sector': 'Sector',
            'village': 'Village',
            'post':'post',
            'thana': 'Police Station',
            'district': 'District',
            'division': 'Division',
        }
        widgets = {f: forms.TextInput(attrs={'class': INPUT_CLASSES}) for f in fields}



# -------------------------------
# 🔹 Company Assign Form
# -------------------------------
class CompanySelectForm(forms.ModelForm):
    class Meta:
        model = ForceMember
        fields = ['company'] 




from django import forms
from .models import Duty

class DutyForm(forms.ModelForm):
    member_no = forms.IntegerField(
        label="Member No",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'border-2 border-blue-400 rounded p-2 w-full'})
    )
    members = forms.ModelMultipleChoiceField(
        queryset=ForceMember.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'border-2 border-blue-400 rounded p-2 w-full h-40'
        })
    )

    class Meta:
        model = Duty
        fields = ['member_no', 'members', 'date', 'start_time', 'end_time', 'destination']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'border-2 border-blue-400 rounded p-2 w-full'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'border-2 border-blue-400 rounded p-2 w-full'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'border-2 border-blue-400 rounded p-2 w-full'}),
            'destination': forms.TextInput(attrs={'class': 'border-2 border-blue-400 rounded p-2 w-full'}),
        }
