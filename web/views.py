from django.shortcuts import render
from. models import Article, Comment, Visitor
# Create your views here.
def home(request):
    articles = Article.objects.all()
    return render(request, 'base.html', {'articles': articles})

def articles(request):
    return render(request, 'articles.html')
