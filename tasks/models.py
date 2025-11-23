from django.db import models
from datetime import date, time
# -------------------------------
# 🔹 All Force 
# -------------------------------
class ForceMember(models.Model):
    COM_CHOICES = [
        ('OTHER', '......'),
        ('cpc-1', 'CPC-1'),
        ('cpc-2', 'CPC-2'),
        ('cpc-3', 'CPC-3'),
        ('cpsc', 'CPSC'),
        ('hq', 'HQ'),
        ('Bn HQ', 'Bn HQ'),
        ('ro', 'RO'), 
        ('mi', 'Mi'), 
        ('ab', 'A Branch'), 
    ]

    RANK_CHOICES = [
        ('OTHER', '......'),
        ('OFFICER', 'Offr'),
        ('DAD', 'DAD'),
        ('SI', 'SI'),
        ('ASI', 'ASI'),
        ('NAYEK', 'Nek'),
        ('CONSTABLE', 'Con'),
        ('CIVIL', 'Civ'),
    ]
    FORCE_CHOICES = [
        ('OTHER', '......'),
        ('ARMY', 'Army'),
        ('NAVY', 'Navy'),
        ('AIR', 'Air'),
        ('POLICE', 'Police'),
        ('BGB', 'BGB'),
        ('VDP', 'Ansar VDP'),
        ('CIV', 'Civ'),
    ]

    no = models.IntegerField(unique=True)
    name = models.CharField(max_length=50)
    rank = models.CharField(max_length=20, choices=RANK_CHOICES)
    force = models.CharField(max_length=20, choices=FORCE_CHOICES)

    company = models.CharField(max_length=50, choices=COM_CHOICES, blank=True, null=True)

    svc_join = models.DateField()
    mother_unit = models.CharField(max_length=50, default="Unknown")
    rab_join = models.DateField()
    birth_day = models.DateField()  

    nid = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    wf_phone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.get_rank_display()} - {self.name}"

# -------------------------------
# 🔹 Present Address
# -------------------------------
class PresentAddress(models.Model):
    member = models.OneToOneField(
        ForceMember,
        on_delete=models.CASCADE,
        related_name='present_address'
    )
    house = models.CharField(max_length=20)
    road = models.CharField(max_length=20)
    sector = models.CharField(max_length=20)
    village = models.CharField(max_length=20)
    post = models.CharField(max_length=20, default="N/A")
    thana = models.CharField(max_length=30)
    district = models.CharField(max_length=30)
    division = models.CharField(max_length=30)

    def __str__(self):
        return f"Present Address of {self.member.name}"

# -------------------------------
# 🔹 Permanent Address
# -------------------------------
class PermanentAddress(models.Model):
    member = models.OneToOneField(
        ForceMember,
        on_delete=models.CASCADE,
        related_name='permanent_address'
    )
    house = models.CharField(max_length=20)
    road = models.CharField(max_length=20)
    sector = models.CharField(max_length=20)
    village = models.CharField(max_length=20)
    post = models.CharField(max_length=20, default="N/A")
    thana = models.CharField(max_length=30)
    district = models.CharField(max_length=30)
    division = models.CharField(max_length=30)

    def __str__(self):
        return f"Permanent Address of {self.member.name}"

# -------------------------------
# 🔹 Other Related Models (Duty, MI, Ro, AcctBr, TrgBr, Mt)
# -------------------------------
class AcctBr(models.Model):
    member = models.ForeignKey(ForceMember, on_delete=models.CASCADE, related_name='acctbr')
    destination = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.member.name} → {self.destination}"

class Ro(models.Model):
    member = models.ForeignKey(ForceMember, on_delete=models.CASCADE, related_name='ro')
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class MiRoomVisit(models.Model):
    member = models.ForeignKey(ForceMember, on_delete=models.CASCADE, related_name='mi_visits')
    symptoms = models.TextField()
    date = models.DateField(auto_now_add=True)
    treatment = models.TextField()

    def __str__(self):
        return f"{self.member.name} - {self.date}"

class Duty(models.Model):
    member = models.ForeignKey('ForceMember', on_delete=models.CASCADE, related_name='duties')
    name = models.CharField(max_length=20)
    rank = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    destination = models.CharField(max_length=50, default="N/A")
    date = models.DateField(default=date.today)
    start_time = models.TimeField(default=time(8,0))
    end_time = models.TimeField()
    serial_no = models.CharField(max_length=10, blank=True, null=True, unique=True)

    def save(self, *args, **kwargs):
        # member থেকে স্বয়ংক্রিয়ভাবে নাম, পদবী, ফোন নেওয়া 
        if self.member:
            self.name = self.member.name
            self.rank = self.member.get_rank_display()
            self.phone = self.member.phone

        # serial_no স্বয়ংক্রিয়
        if not self.serial_no:
            last_duty = Duty.objects.all().order_by('-id').first()
            if last_duty and last_duty.serial_no:
                self.serial_no = str(int(last_duty.serial_no)+1)
            else:
                self.serial_no = "0000001"

        super().save(*args, **kwargs)


class Mt(models.Model):
    member = models.ForeignKey(ForceMember, on_delete=models.CASCADE, related_name='mt')
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class TrgBr(models.Model):
    member = models.ForeignKey(ForceMember, on_delete=models.CASCADE, related_name='trg')
    rab_id = models.IntegerField(unique=True)

    def __str__(self):
        return f"TRG for {self.member.name} ({self.rab_id})"



class MemberPosting(models.Model):
    member = models.ForeignKey("ForceMember", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default="pending")

    def __str__(self):
        return f"{self.member.name} - {self.status}"
