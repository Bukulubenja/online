from django.urls import path

from . import views

urlpatterns = [
    path('', views.student_schedule, name='schedule'),
    path('book/<int:session_id>/', views.book_session, name='book_session'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('teacher/', views.teacher_schedule, name='teacher_schedule'),
    path('teacher/new/', views.create_session, name='create_session'),
]
