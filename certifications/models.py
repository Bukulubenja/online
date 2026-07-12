from datetime import date

from django.conf import settings
from django.db import models

from courses.models import LEVEL_CHOICES


SECTION_CHOICES = [
    ('listening', 'Listening'),
    ('reading', 'Reading'),
    ('writing', 'Writing'),
    ('speaking', 'Speaking'),
]


class Exam(models.Model):
    level = models.CharField(max_length=2, choices=LEVEL_CHOICES, unique=True)
    title = models.CharField(max_length=200)
    duration_minutes = models.PositiveIntegerField(default=60)
    passing_score = models.PositiveIntegerField(default=60)
    fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ['level']

    def __str__(self):
        return f'{self.title} ({self.level})'


class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    section = models.CharField(max_length=20, choices=SECTION_CHOICES)
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.exam.level} - {self.text[:50]}'


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class ExamAttempt(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exam_attempts')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='attempts')
    registered_at = models.DateTimeField(auto_now_add=True)
    fee_paid = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True)
    score = models.PositiveIntegerField(null=True, blank=True)
    passed = models.BooleanField(null=True)

    def __str__(self):
        return f'{self.student} - {self.exam}'


class ExamAnswer(models.Model):
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    selected_choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('attempt', 'question')

    def __str__(self):
        return f'{self.attempt} - {self.question}'


class Certificate(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificates')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='certificates')
    certificate_id = models.CharField(max_length=40, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)

    def __str__(self):
        return self.certificate_id

    @staticmethod
    def generate_id(level):
        year = date.today().year
        seq = Certificate.objects.count() + 1
        return f'FR-{level}-{year}-{seq:06d}'
