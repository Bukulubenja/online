from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from courses.models import Course
from enrollments.models import Enrollment

from .models import Booking, ClassSession


def _teacher_check(user):
    return user.role == 'teacher' or user.is_superuser


def session_json(session, with_seats=True):
    data = {
        'id': session.id,
        'course': session.course.title,
        'course_slug': session.course.slug,
        'teacher': session.teacher.get_full_name() or session.teacher.username,
        'start_time': session.start_time,
        'end_time': session.end_time,
        'capacity': session.capacity,
    }
    if with_seats:
        data['seats_left'] = session.seats_left
    return data


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_schedule(request):
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

    return Response({
        'my_bookings': [
            {'booking_id': b.id, **session_json(b.session, with_seats=False)}
            for b in my_bookings
        ],
        'available_sessions': [session_json(s) for s in available_sessions],
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_book_session(request, session_id):
    session = get_object_or_404(ClassSession, id=session_id)

    if not Enrollment.objects.filter(student=request.user, course=session.course).exists():
        return Response({'detail': 'Enroll in this course to book its classes.'}, status=403)

    enrollment = Enrollment.objects.get(student=request.user, course=session.course)

    if Booking.objects.filter(session=session, student=request.user, status='booked').exists():
        return Response({'detail': 'You already booked this class.'}, status=400)

    if session.seats_left <= 0:
        return Response({'detail': 'This class is full.'}, status=400)

    booking = Booking.objects.create(session=session, student=request.user, enrollment=enrollment)
    return Response({'booking_id': booking.id}, status=201)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, student=request.user)
    booking.status = 'cancelled'
    booking.save()
    return Response(status=204)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_teacher_schedule(request):
    if not _teacher_check(request.user):
        return Response({'detail': 'Teacher access only.'}, status=403)

    sessions = ClassSession.objects.filter(teacher=request.user).select_related('course').prefetch_related(
        'bookings', 'trial_bookings'
    )
    rows = []
    for session in sessions:
        rows.append({
            **session_json(session, with_seats=False),
            'booked_count': sum(1 for b in session.bookings.all() if b.status == 'booked'),
            'trial_count': sum(1 for t in session.trial_bookings.all() if t.status != 'cancelled'),
        })
    return Response(rows)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_create_session(request):
    if not _teacher_check(request.user):
        return Response({'detail': 'Teacher access only.'}, status=403)

    course = get_object_or_404(Course, id=request.data.get('course'), instructor=request.user)
    start_time = request.data.get('start_time')
    end_time = request.data.get('end_time')
    capacity = request.data.get('capacity') or 1

    if not start_time or not end_time:
        return Response({'detail': 'Start and end time are required.'}, status=400)

    session = ClassSession.objects.create(
        course=course, teacher=request.user, start_time=start_time, end_time=end_time, capacity=capacity,
    )
    return Response(session_json(session, with_seats=False), status=201)
