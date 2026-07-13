from django.db import models

from courses.models import LEVEL_CHOICES

# Create your models here.


class Article(models.Model):
    CATEGORY_CHOICES = [
        ('vocabulary', 'Vocabulary'),
        ('grammar', 'Grammar'),
        ('culture', 'Culture'),
        ('travel', 'Travel'),
        ('food', 'Food'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='articles/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    author = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author} on {self.created_at.strftime("%Y-%m-%d %H:%M:%S")}'


class Visitor(models.Model):
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Feedback from {self.email} on {self.created_at.strftime("%Y-%m-%d %H:%M:%S")}'


class TrialBooking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=32, blank=True)
    preferred_level = models.CharField(max_length=2, choices=LEVEL_CHOICES, blank=True)
    session = models.ForeignKey(
        'schedules.ClassSession',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trial_bookings',
    )
    preferred_date = models.DateField(null=True, blank=True)
    preferred_time = models.TimeField(null=True, blank=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        when = self.session.start_time if self.session_id else self.preferred_date
        return f'{self.name} - trial on {when} ({self.status})'