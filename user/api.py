from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from enrollments.models import LessonProgress
from .models import User
from .services import AccountCreationError, create_student_account, create_teacher_application


def user_json(user):
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'full_name': f'{user.first_name} {user.last_name}'.strip(),
        'phone': user.phone,
        'role': user.role,
        'is_superuser': user.is_superuser,
        'current_level': user.current_level,
        'current_level_display': user.get_current_level_display(),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def api_register(request):
    data = request.data
    full_name = (data.get('full_name') or '').strip()
    email = (data.get('email') or '').strip()
    phone = (data.get('phone') or '').strip()
    current_level = (data.get('current_level') or '').strip()
    password = data.get('password') or ''

    try:
        user = create_student_account(
            email, password, full_name=full_name, phone=phone, current_level=current_level,
        )
    except AccountCreationError as e:
        return Response({'detail': ' '.join(e.messages)}, status=400)

    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key, 'user': user_json(user)}, status=201)


@api_view(['POST'])
@permission_classes([AllowAny])
def api_apply_teacher(request):
    data = request.data
    full_name = (data.get('full_name') or '').strip()
    email = (data.get('email') or '').strip()
    phone = (data.get('phone') or '').strip()
    password = data.get('password') or ''

    try:
        create_teacher_application(email, password, full_name=full_name, phone=phone)
    except AccountCreationError as e:
        return Response({'detail': ' '.join(e.messages)}, status=400)

    return Response({'detail': 'Application submitted. It is pending Main Admin review.'}, status=201)


@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    username = (request.data.get('username') or '').strip()
    password = request.data.get('password') or ''
    user = authenticate(request, username=username, password=password)
    if user is None:
        if User.objects.filter(username=username, is_active=False, role='teacher').exists():
            return Response({'detail': 'Your instructor application is pending review.'}, status=400)
        return Response({'detail': 'Invalid username or password.'}, status=400)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key, 'user': user_json(user)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    request.user.auth_token.delete()
    return Response(status=204)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_dashboard(request):
    enrollments = list(request.user.enrollments.select_related('course').order_by('-enrolled_at'))
    completed_lessons = LessonProgress.objects.filter(enrollment__student=request.user).count()
    certificates_count = request.user.certificates.filter(is_valid=True).count()
    avg_progress = round(sum(e.progress_percent for e in enrollments) / len(enrollments)) if enrollments else 0
    continue_enrollment = next((e for e in enrollments if e.progress_percent < 100), None)
    return Response({
        'user': user_json(request.user),
        'enrollments_count': len(enrollments),
        'completed_lessons': completed_lessons,
        'certificates_count': certificates_count,
        'avg_progress': avg_progress,
        'continue_course_slug': continue_enrollment.course.slug if continue_enrollment else None,
    })
