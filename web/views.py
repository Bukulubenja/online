from django.shortcuts import get_object_or_404, render
from. models import Article, Comment, Visitor
# Create your views here.
def home(request):
    articles = Article.objects.order_by('-created_at')
    latest_article = articles.first()
    other_articles = articles.exclude(pk=latest_article.pk) if latest_article else articles
    return render(request, 'base.html', {
        'articles': other_articles,
        'latest_article': latest_article,
    })

def articles(request):
    articles = Article.objects.order_by('-created_at')
    return render(request, 'articles.html', {'articles': articles})

def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    return render(request, 'article_detail.html', {'article': article})
