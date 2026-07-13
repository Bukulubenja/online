from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from courses.models import Course
from enrollments.models import Enrollment

from .models import Booking, ClassSession


def teacher_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path(), login_url='login')
        if request.user.role != 'teacher' and not request.user.is_superuser:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required(login_url='login')
def student_schedule(request):
    now = timezone.now()

    my_bookings = Booking.objects.filter(
        student=request.user, status='booked', session__start_time__gte=now
    ).select_related('session__course', 'session__teacher')

    booked_session_ids = set(
        Booking.objects.filter(student=request.user, status='booked').values_list('session_id', flat=True)
    )

    enrolled_course_ids = Enrollment.objects.filter(student=request.user).values_list('course_id', flat=True)
    available_sessions = ClassSession.objects.filter(
        course_id__in=enrolled_course_ids, start_time__gte=now
    ).exclude(id__in=booked_session_ids).select_related('course', 'teacher')

    return render(request, 'schedule.html', {
        'my_bookings': my_bookings,
        'available_sessions': available_sessions,
    })


@login_required(login_url='login')
@require_POST
def book_session(request, session_id):
    session = get_object_or_404(ClassSession, id=session_id)

    if not Enrollment.objects.filter(student=request.user, course=session.course).exists():
        messages.error(request, 'Enroll in this course to book its classes.')
        return redirect('schedule')

    enrollment = Enrollment.objects.get(student=request.user, course=session.course)

    if Booking.objects.filter(session=session, student=request.user, status='booked').exists():
        messages.error(request, 'You already booked this class.')
        return redirect('schedule')

    if session.seats_left <= 0:
        messages.error(request, 'This class is full.')
        return redirect('schedule')

    Booking.objects.create(session=session, student=request.user, enrollment=enrollment)
    messages.success(request, 'Class booked and added to your timetable.')
    return redirect('schedule')


@login_required(login_url='login')
@require_POST
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, student=request.user)
    booking.status = 'cancelled'
    booking.save()
    messages.success(request, 'Booking cancelled.')
    return redirect('schedule')


@teacher_required
def teacher_schedule(request):
    sessions = ClassSession.objects.filter(teacher=request.user).select_related('course').prefetch_related(
        'bookings', 'trial_bookings'
    )
    rows = [
        {
            'session': session,
            'booked_count': sum(1 for b in session.bookings.all() if b.status == 'booked'),
            'trial_count': sum(1 for t in session.trial_bookings.all() if t.status != 'cancelled'),
        }
        for session in sessions
    ]
    return render(request, 'teacher_schedule.html', {'rows': rows})


@teacher_required
def create_session(request):
    courses = Course.objects.filter(instructor=request.user)

    if request.method == 'POST':
        course = get_object_or_404(Course, id=request.POST.get('course'), instructor=request.user)
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        capacity = request.POST.get('capacity') or 1

        if not start_time or not end_time:
            messages.error(request, 'Start and end time are required.')
            return redirect('create_session')

        ClassSession.objects.create(
            course=course,
            teacher=request.user,
            start_time=start_time,
            end_time=end_time,
            capacity=capacity,
        )
        messages.success(request, 'Class session added to the timetable.')
        return redirect('teacher_schedule')

    return render(request, 'create_session.html', {'courses': courses})
