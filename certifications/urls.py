from django.urls import path

from . import views

urlpatterns = [
    path('certifications/', views.exam_list, name='exam_list'),
    path('certifications/<str:level>/', views.exam_detail, name='exam_detail'),
    path('certificate/<str:certificate_id>/', views.certificate_verify, name='certificate_verify'),

    path('portal/exams/', views.my_exams, name='my_exams'),
    path('portal/exams/<str:level>/register/', views.register_exam, name='register_exam'),
    path('portal/exam/<int:attempt_id>/', views.take_exam, name='take_exam'),
    path('portal/exam/<int:attempt_id>/submit/', views.submit_exam, name='submit_exam'),
    path('portal/exam/<int:attempt_id>/result/', views.exam_result, name='exam_result'),
    path('portal/certificates/', views.my_certificates, name='my_certificates'),
]
