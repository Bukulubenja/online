
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from courses.views import CourseViewSet
from user import api as user_api
from enrollments import api as enrollments_api
from assignments import api as assignments_api
from schedules import api as schedules_api
from payments import api as payments_api
from certifications import api as certifications_api
from dashboard import api as dashboard_api

router = DefaultRouter()
router.register('courses', CourseViewSet, basename='course-api')

api_urlpatterns = [
    path('auth/register/', user_api.api_register, name='api_register'),
    path('auth/apply-teacher/', user_api.api_apply_teacher, name='api_apply_teacher'),
    path('auth/login/', user_api.api_login, name='api_login'),
    path('auth/logout/', user_api.api_logout, name='api_logout'),
    path('auth/me/', user_api.api_dashboard, name='api_dashboard'),

    path('courses/<slug:slug>/enroll/', enrollments_api.api_enroll, name='api_enroll'),
    path('my-courses/', enrollments_api.api_my_courses, name='api_my_courses'),
    path('materials/', enrollments_api.api_materials, name='api_materials'),
    path('lessons/<int:lesson_id>/', enrollments_api.api_lesson_detail, name='api_lesson_detail'),
    path('lessons/<int:lesson_id>/complete/', enrollments_api.api_mark_complete, name='api_mark_complete'),

    path('assignments/', assignments_api.api_assignment_list, name='api_assignment_list'),
    path('assignments/<int:pk>/', assignments_api.api_assignment_detail, name='api_assignment_detail'),
    path('assignments/<int:pk>/submit/', assignments_api.api_submit_assignment, name='api_submit_assignment'),

    path('schedule/', schedules_api.api_schedule, name='api_schedule'),
    path('schedule/book/<int:session_id>/', schedules_api.api_book_session, name='api_book_session'),
    path('schedule/cancel/<int:booking_id>/', schedules_api.api_cancel_booking, name='api_cancel_booking'),
    path('schedule/teacher/', schedules_api.api_teacher_schedule, name='api_teacher_schedule'),
    path('schedule/teacher/courses/', schedules_api.api_teacher_courses, name='api_teacher_courses'),
    path('schedule/teacher/new/', schedules_api.api_create_session, name='api_create_session'),

    path('courses/<slug:slug>/checkout/', payments_api.api_checkout, name='api_checkout'),
    path('payments/<int:payment_id>/confirm/', payments_api.api_confirm_payment, name='api_confirm_payment'),
    path('payments/<int:payment_id>/', payments_api.api_receipt, name='api_receipt'),

    path('exams/', certifications_api.api_exam_list, name='api_exam_list'),
    path('exams/mine/', certifications_api.api_my_exams, name='api_my_exams'),
    path('exams/<str:level>/register/', certifications_api.api_register_exam, name='api_register_exam'),
    path('exam-attempts/<int:attempt_id>/', certifications_api.api_take_exam, name='api_take_exam'),
    path('exam-attempts/<int:attempt_id>/submit/', certifications_api.api_submit_exam, name='api_submit_exam'),
    path('exam-attempts/<int:attempt_id>/result/', certifications_api.api_exam_result, name='api_exam_result'),
    path('certificates/mine/', certifications_api.api_my_certificates, name='api_my_certificates'),
    path('certificates/<str:certificate_id>/', certifications_api.api_certificate_verify, name='api_certificate_verify'),

    path('admin/students/', dashboard_api.api_admin_students, name='api_admin_students'),
    path('admin/instructors/', dashboard_api.api_admin_instructors, name='api_admin_instructors'),
    path('admin/instructors/<int:user_id>/approve/', dashboard_api.api_admin_instructor_approve, name='api_admin_instructor_approve'),
    path('admin/instructors/<int:user_id>/reject/', dashboard_api.api_admin_instructor_reject, name='api_admin_instructor_reject'),

    path('', include(router.urls)),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('web.urls')),
    path('user/', include('user.urls')),
    path('courses/', include('courses.urls')),
    path('portal/', include('enrollments.urls')),
    path('payments/', include('payments.urls')),
    path('', include('certifications.urls')),
    path('', include('dashboard.urls')),
    path('assignments/', include('assignments.urls')),
    path('portal/schedule/', include('schedules.urls')),
    path('api/', include(api_urlpatterns)),

]

urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
