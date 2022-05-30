from django.contrib import admin
from .models import *
from django.contrib import admin
# Register your models here.

class ManagerAdmin(admin.ModelAdmin):
    list_display = ('id','driver_id','db_name','token')

admin.site.register(Manager,ManagerAdmin)