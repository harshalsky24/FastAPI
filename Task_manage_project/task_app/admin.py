from django.contrib import admin
from .models import Task,Team,Role

# Register your models here.
# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ['id','username','email','password']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id','title','description','status','priority','created_at','updated_at','deadline','creator','assignee', 'reviewer','team']

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['id','name','description']

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['id','user','team','role']