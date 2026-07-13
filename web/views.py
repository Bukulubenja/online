from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from courses.models import LEVEL_CHOICES
from schedules.models import ClassSession

from. models import Article, Comment, TrialBooking, Visitor
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
    if request.method == 'POST':
        author = request.POST.get('author', '').strip()
        content = request.POST.get('content', '').strip()
        if not author or not content:
            messages.error(request, 'Please add your name and a comment.')
            return redirect('article_detail', pk=pk)
        Comment.objects.create(article=article, author=author, content=content)
        messages.success(request, 'Your comment has been posted.')
        return redirect('article_detail', pk=pk)
    return render(request, 'article_detail.html', {
        'article': article,
        'comments': article.comments.all(),
    })


def subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            Visitor.objects.create(email=email)
            messages.success(request, "You're subscribed! Watch your inbox for weekly French lessons.")
        else:
            messages.error(request, 'Please enter a valid email address.')
    return redirect('home')


def book_trial(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        session_id = request.POST.get('session_id')
        preferred_date = request.POST.get('preferred_date') or None
        preferred_time = request.POST.get('preferred_time') or None

        if not name or not email:
            messages.error(request, 'Name and email are required.')
            return redirect('book_trial')

        session = None
        if session_id:
            session = get_object_or_404(ClassSession, id=session_id)
            if session.seats_left <= 0:
                messages.error(request, 'Sorry, that class just filled up - pick another one.')
                return redirect('book_trial')
        elif not (preferred_date and preferred_time):
            messages.error(request, 'Pick an open class, or enter a preferred date and time.')
            return redirect('book_trial')

        TrialBooking.objects.create(
            name=name,
            email=email,
            phone=request.POST.get('phone', '').strip(),
            preferred_level=request.POST.get('preferred_level', ''),
            session=session,
            preferred_date=preferred_date,
            preferred_time=preferred_time,
            message=request.POST.get('message', '').strip(),
        )
        messages.success(request, "Thanks! Your free trial request has been received - we'll email you to confirm the time.")
        return redirect('book_trial')

    now = timezone.now()
    open_sessions = [
        s for s in ClassSession.objects.filter(start_time__gte=now).select_related('course', 'teacher')
        if s.seats_left > 0
    ]
    return render(request, 'book_trial.html', {'level_choices': LEVEL_CHOICES, 'open_sessions': open_sessions})
