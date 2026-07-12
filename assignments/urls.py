from django.urls import path

from . import views

urlpatterns = [
    path('', views.assignment_list, name='assignments'),
    path('<int:pk>/', views.assignment_detail, name='assignment_detail'),
    path('<int:pk>/submit/', views.submit_assignment, name='submit_assignment'),
]
