from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from user.models import User
from user.services import AccountCreationError, create_student_account


def _main_admin_check(user):
    return user.role == 'main_admin' or user.is_superuser


def student_json(student):
    return {
        'id': student.id,
        'username': student.username,
        'email': student.email,
        'full_name': f'{student.first_name} {student.last_name}'.strip(),
        'phone': student.phone,
        'current_level': student.current_level,
        'date_joined': student.date_joined,
    }


def instructor_json(teacher):
    return {
        'id': teacher.id,
        'username': teacher.username,
        'email': teacher.email,
        'full_name': f'{teacher.first_name} {teacher.last_name}'.strip(),
        'phone': teacher.phone,
        'is_active': teacher.is_active,
        'date_joined': teacher.date_joined,
    }


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def api_admin_students(request):
    if not _main_admin_check(request.user):
        return Response({'detail': 'Main Admin access only.'}, status=403)

    if request.method == 'POST':
        data = request.data
        try:
            student = create_student_account(
                data.get('email'), data.get('password') or '',
                full_name=data.get('full_name'), phone=data.get('phone'),
                current_level=data.get('current_level'),
            )
        except AccountCreationError as e:
            return Response({'detail': ' '.join(e.messages)}, status=400)
        return Response(student_json(student), status=201)

    query = (request.GET.get('q') or '').strip()
    students = User.objects.filter(role='student').order_by('-date_joined')
    if query:
        students = students.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
            | Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )
    return Response([student_json(s) for s in students])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_admin_instructors(request):
    if not _main_admin_check(request.user):
        return Response({'detail': 'Main Admin access only.'}, status=403)

    return Response({
        'pending': [instructor_json(t) for t in User.objects.filter(role='teacher', is_active=False).order_by('-date_joined')],
        'approved': [instructor_json(t) for t in User.objects.filter(role='teacher', is_active=True).order_by('-date_joined')],
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_admin_instructor_approve(request, user_id):
    if not _main_admin_check(request.user):
        return Response({'detail': 'Main Admin access only.'}, status=403)

    teacher = get_object_or_404(User, id=user_id, role='teacher', is_active=False)
    teacher.is_active = True
    teacher.save(update_fields=['is_active'])
    return Response(instructor_json(teacher))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_admin_instructor_reject(request, user_id):
    if not _main_admin_check(request.user):
        return Response({'detail': 'Main Admin access only.'}, status=403)

    teacher = get_object_or_404(User, id=user_id, role='teacher', is_active=False)
    teacher.delete()
    return Response(status=204)
