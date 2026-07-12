from django.conf import settings
from django.db import models

from courses.models import Course, Lesson


class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f'{self.student} -> {self.course}'

    @property
    def progress_percent(self):
        total = Lesson.objects.filter(module__course=self.course).count()
        if total == 0:
            return 0
        completed = self.lesson_progress.count()
        return round(completed * 100 / total)


class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress_entries')
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('enrollment', 'lesson')

    def __str__(self):
        return f'{self.enrollment.student} completed {self.lesson}'
