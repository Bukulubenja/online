from django.contrib import admin

from .models import Assignment, Submission


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'points', 'due_at')
    list_filter = ('lesson__module__course',)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'submitted_at', 'grade')
    list_filter = ('assignment',)
    list_editable = ('grade',)
