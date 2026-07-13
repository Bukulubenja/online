from django.conf import settings
from django.db import models

from courses.models import Course


class ClassSession(models.Model):
    """A single bookable class slot for a course - the building block of each
    learner's customized timetable (they book only the sessions that fit them,
    rather than following one fixed cohort schedule)."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='class_sessions')
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'teacher'},
        related_name='sessions_taught',
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    capacity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f'{self.course.title} with {self.teacher} @ {self.start_time:%Y-%m-%d %H:%M}'

    @property
    def seats_left(self):
        booked = self.bookings.filter(status='booked').count()
        trial = self.trial_bookings.exclude(status='cancelled').count()
        return self.capacity - booked - trial


class Booking(models.Model):
    STATUS_CHOICES = [
        ('booked', 'Booked'),
        ('cancelled', 'Cancelled'),
    ]

    session = models.ForeignKey(ClassSession, on_delete=models.CASCADE, related_name='bookings')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='class_bookings')
    enrollment = models.ForeignKey(
        'enrollments.Enrollment', on_delete=models.CASCADE, related_name='class_bookings'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='booked')
    booked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['session__start_time']

    def __str__(self):
        return f'{self.student} -> {self.session}'
