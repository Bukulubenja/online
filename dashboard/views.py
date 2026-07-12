from datetime import timedelta
from functools import wraps

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone

from certifications.models import Certificate, ExamAttempt
from courses.models import Course
from enrollments.models import Enrollment
from payments.models import Payment

User = get_user_model()


def main_admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path(), login_url='login')
        if not (request.user.role == 'main_admin' or request.user.is_superuser):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


@main_admin_required
def admin_dashboard(request):
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    thirty_days_ago = now - timedelta(days=30)

    total_students = User.objects.filter(role='student').count()
    new_students = User.objects.filter(role='student', date_joined__gte=thirty_days_ago).count()

    total_courses = Course.objects.count()
    published_courses = Course.objects.filter(is_published=True).count()

    enrollments = Enrollment.objects.select_related('course')
    total_enrollments = enrollments.count()
    completed_enrollments = sum(1 for e in enrollments if e.progress_percent == 100)
    completion_rate = round(completed_enrollments * 100 / total_enrollments) if total_enrollments else 0

    successful_payments = Payment.objects.filter(status='success')
    total_revenue = successful_payments.aggregate(total=Sum('amount'))['total'] or 0
    monthly_revenue = successful_payments.filter(created_at__gte=month_start).aggregate(total=Sum('amount'))['total'] or 0

    payment_counts = {
        'success': Payment.objects.filter(status='success').count(),
        'pending': Payment.objects.filter(status='pending').count(),
        'failed': Payment.objects.filter(status='failed').count(),
    }
    recent_payments = successful_payments.select_related('student', 'course').order_by('-created_at')[:5]

    certificates_issued = Certificate.objects.filter(is_valid=True).count()
    submitted_attempts = ExamAttempt.objects.filter(submitted_at__isnull=False)
    submitted_count = submitted_attempts.count()
    passed_count = submitted_attempts.filter(passed=True).count()
    pass_rate = round(passed_count * 100 / submitted_count) if submitted_count else 0

    instructors = []
    for teacher in User.objects.filter(role='teacher'):
        courses_taught = teacher.courses_taught.all()
        course_count = courses_taught.count()
        student_count = Enrollment.objects.filter(course__in=courses_taught).count()
        instructors.append({
            'teacher': teacher,
            'course_count': course_count,
            'student_count': student_count,
        })

    context = {
        'total_students': total_students,
        'new_students': new_students,
        'total_courses': total_courses,
        'published_courses': published_courses,
        'total_enrollments': total_enrollments,
        'completion_rate': completion_rate,
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'payment_counts': payment_counts,
        'recent_payments': recent_payments,
        'certificates_issued': certificates_issued,
        'submitted_count': submitted_count,
        'pass_rate': pass_rate,
        'instructors': instructors,
    }
    return render(request, 'admin_dashboard.html', context)
