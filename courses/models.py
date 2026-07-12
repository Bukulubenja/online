from django.conf import settings
from django.db import models


LEVEL_CHOICES = [
    ('A1', 'A1 - Beginner'),
    ('A2', 'A2 - Elementary'),
    ('B1', 'B1 - Intermediate'),
    ('B2', 'B2 - Upper Intermediate'),
    ('C1', 'C1 - Advanced'),
    ('C2', 'C2 - Mastery'),
]


class Course(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    level = models.CharField(max_length=2, choices=LEVEL_CHOICES)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='courses/', blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'teacher'},
        related_name='courses_taught',
    )
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['level', 'title']

    def __str__(self):
        return f'{self.title} ({self.level})'


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.course.title} - Module {self.order}: {self.title}'


class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    video_url = models.URLField(blank=True)
    pdf = models.FileField(upload_to='lessons/pdfs/', blank=True)
    content = models.TextField(blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.module.title} - {self.title}'


class Material(models.Model):
    TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('audio', 'Audio'),
        ('video', 'Video'),
        ('article', 'Article'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    material_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    file = models.FileField(upload_to='materials/', blank=True)
    external_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.title} ({self.course.title})'
