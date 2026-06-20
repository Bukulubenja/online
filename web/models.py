from django.db import models

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
    author = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author} on {self.created_at.strftime("%Y-%m-%d %H:%M:%S")}'


class Visitor(models.Model):
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Feedback from {self.name} on {self.created_at.strftime("%Y-%m-%d %H:%M:%S")}'