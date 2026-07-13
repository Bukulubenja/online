from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('articles/', views.articles, name='articles'),
    path('articles/<int:pk>/', views.article_detail, name='article_detail'),
    path('book-trial/', views.book_trial, name='book_trial'),
    path('subscribe/', views.subscribe, name='subscribe'),

]
