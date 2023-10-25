from django.db import models

# Create your models here.
class ManagerTracker(models.Model):

    data_api = models.CharField(max_length=5000)
