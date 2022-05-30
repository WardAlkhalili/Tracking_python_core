from django.contrib import admin
from .models import *
from django.contrib import admin
# Register your models here.


class ManagerParentAdmin(admin.ModelAdmin):
    list_display = ('id','user_id','school_id','parent_id','db_name','token')

admin.site.register(ManagerParent,ManagerParentAdmin)