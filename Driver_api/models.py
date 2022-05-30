from django.db import models
from rest_framework.authtoken.models import Token
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
import re


class Manager(models.Model):

    token = models.CharField(max_length=5000)
    db_name = models.CharField(max_length=5000)
    driver_id = models.IntegerField()
        
    def pincode(pin):
        p=re.sub(r'\d+','',pin)
        database_name = re.sub('[QWERTYUIOPASDFGHJKLZXCVBNM]', '', p)
        return database_name  


    def __str__(self):
        return self.token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        auth_token = Token.objects.create(user=instance)
