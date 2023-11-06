from django.contrib import admin
from .models import *
from django.contrib import admin
# Register your models here.


class ManagerParentAdmin(admin.ModelAdmin):
    list_display = ('id','user_id','school_id','parent_id','db_name','token')
    list_display_student = ('id','user_id','school_id','student_id','db_name','token','is_active')
admin.site.register(ManagerParent,ManagerParentAdmin)
admin.site.register(ManagerStudentUni)