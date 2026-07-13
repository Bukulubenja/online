from django.contrib import admin
from .models import Article, Comment, TrialBooking, Visitor
# Register your models here.
admin.site.register(Article)
admin.site.register(Visitor)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'article', 'created_at')
    list_filter = ('article',)


@admin.register(TrialBooking)
class TrialBookingAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'preferred_level', 'session', 'preferred_date', 'preferred_time', 'status', 'created_at')
    list_filter = ('status', 'preferred_level')
    list_editable = ('status',)
    raw_id_fields = ('session',)