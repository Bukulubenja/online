from django.urls import path

from . import views

urlpatterns = [
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/students/', views.admin_students, name='admin_students'),
    path('admin-dashboard/students/new/', views.admin_student_create, name='admin_student_create'),
    path('admin-dashboard/instructors/', views.admin_instructors, name='admin_instructors'),
    path('admin-dashboard/instructors/<int:user_id>/approve/', views.admin_instructor_approve, name='admin_instructor_approve'),
    path('admin-dashboard/instructors/<int:user_id>/reject/', views.admin_instructor_reject, name='admin_instructor_reject'),
]
