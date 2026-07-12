from django.urls import path

from . import views

urlpatterns = [
    path('enroll/<slug:slug>/', views.enroll, name='enroll'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('lesson/<int:lesson_id>/complete/', views.mark_complete, name='mark_complete'),
]
