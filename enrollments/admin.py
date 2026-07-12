from django.contrib import admin

from .models import Enrollment, LessonProgress


class LessonProgressInline(admin.TabularInline):
    model = LessonProgress
    extra = 0


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at')
    list_filter = ('course',)
    inlines = [LessonProgressInline]
