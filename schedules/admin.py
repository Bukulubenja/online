from django.contrib import admin

from .models import Booking, ClassSession


@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = ('course', 'teacher', 'start_time', 'end_time', 'capacity')
    list_filter = ('course', 'teacher')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('student', 'session', 'status', 'booked_at')
    list_filter = ('status', 'session__course')
