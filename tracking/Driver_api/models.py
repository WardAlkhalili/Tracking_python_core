from django.db import models
from rest_framework.authtoken.models import Token
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
import re


class Manager(models.Model):
        
    def pincode(pin):
        p=re.sub(r'\d+','',pin)
        database_name = re.sub('[QWERTYUIOPASDFGHJKLZXCVBNM]', '', p)
        return database_name  


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
