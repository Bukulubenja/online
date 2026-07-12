from django.conf import settings
from django.db import models

from courses.models import Course

METHOD_CHOICES = [
    ('mobile_money', 'Mobile Money'),
    ('bank', 'Bank Transfer'),
    ('card', 'Visa/Mastercard'),
    ('paypal', 'PayPal'),
]

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('success', 'Success'),
    ('failed', 'Failed'),
]


class Payment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.student} - {self.course} - {self.status}'
