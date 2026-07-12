from django.contrib import admin

from .models import Certificate, Choice, Exam, ExamAttempt, Question


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('order', 'section', 'text')


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('level', 'title', 'fee', 'passing_score', 'duration_minutes', 'is_published')
    list_filter = ('is_published',)
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('exam', 'section', 'text', 'order')
    list_filter = ('exam', 'section')
    inlines = [ChoiceInline]


@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'score', 'passed', 'fee_paid', 'registered_at')
    list_filter = ('exam', 'passed', 'fee_paid')


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_id', 'student', 'exam', 'issued_at', 'is_valid')
    list_filter = ('is_valid', 'exam')
