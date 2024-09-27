from django.contrib import admin
from .models import *
from django.contrib import admin
# Register your models here.

class ManagerAdmin(admin.ModelAdmin):
    list_display = ('id','data_api')

admin.site.register(ManagerTracker,ManagerAdmin)
# Register your models here.
