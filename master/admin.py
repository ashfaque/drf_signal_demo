from django.contrib import admin
from .models import College, Plan, CollegePlanMapping
# Register your models here.

@admin.register(College)
class College(admin.ModelAdmin):
    list_display = [field.name for field in College._meta.fields]
    search_fields = ('code', 'name')

@admin.register(Plan)
class Plan(admin.ModelAdmin):
    list_display = [field.name for field in Plan._meta.fields]
    search_fields = ('code', 'name')

@admin.register(CollegePlanMapping)
class CollegePlanMapping(admin.ModelAdmin):
    list_display = [field.name for field in CollegePlanMapping._meta.fields]
    search_fields = ('plan__code', 'plan__name', 'college__code', 'college__name')
