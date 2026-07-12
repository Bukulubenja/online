from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('main_admin', 'Main Admin'),
        ('teacher', 'Teacher'),
        ('content_manager', 'Content Manager'),
        ('finance', 'Finance Officer'),
        ('support', 'Support Staff'),
        ('student', 'Student'),
    ]

    LEVEL_CHOICES = [
        ('A1', 'A1 - Beginner'),
        ('A2', 'A2 - Elementary'),
        ('B1', 'B1 - Intermediate'),
        ('B2', 'B2 - Upper Intermediate'),
        ('C1', 'C1 - Advanced'),
        ('C2', 'C2 - Mastery'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    current_level = models.CharField(max_length=2, choices=LEVEL_CHOICES, blank=True)
    phone = models.CharField(max_length=32, blank=True)

    def __str__(self):
        return self.username
