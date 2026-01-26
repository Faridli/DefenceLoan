from django.contrib.auth.models import User

from django.db.models.signals import post_save,pre_save,post_delete 
from django.dispatch import receiver 
from django.core.mail import send_mail



@receiver(post_save, sender=User)
def assign_role(sender, instance, created, **kwargs):
    if created: 

