from django.conf import settings
from django.db import models

from courses.models import Lesson


class Assignment(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    instructions = models.TextField()
    points = models.PositiveIntegerField(default=10)
    due_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['due_at']

    def __str__(self):
        return f'{self.title} ({self.lesson.module.course.title})'


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assignment_submissions')
    content = models.TextField(blank=True)
    file = models.FileField(upload_to='submissions/', blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.PositiveIntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f'{self.student} - {self.assignment}'
