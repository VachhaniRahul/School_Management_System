from django.contrib import admin
from .models import Teacher, Class, Subject, TeachingAssignment, Assignment

# Register your models here.
class SubjectShow(admin.ModelAdmin):
    list_display = ['name', 'code']

class TeachingAssignmentShow(admin.ModelAdmin):
    list_display = ['teacher', 'class_model', 'subject']

admin.site.register(Teacher)
admin.site.register(Class)
admin.site.register(Subject,SubjectShow)
admin.site.register(TeachingAssignment,TeachingAssignmentShow)
admin.site.register(Assignment)

