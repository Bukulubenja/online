from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from courses.models import Course, Lesson, Material

from .models import Enrollment, LessonProgress


def enrollment_json(enrollment):
    course = enrollment.course
    return {
        'id': enrollment.id,
        'course': {
            'id': course.id,
            'title': course.title,
            'slug': course.slug,
            'level': course.level,
            'level_display': course.get_level_display(),
            'thumbnail': course.thumbnail.url if course.thumbnail else None,
        },
        'enrolled_at': enrollment.enrolled_at,
        'progress_percent': enrollment.progress_percent,
    }


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_enroll(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    if course.price > 0:
        return Response({'detail': 'This course requires payment.', 'requires_payment': True}, status=400)
    enrollment, _ = Enrollment.objects.get_or_create(student=request.user, course=course)
    return Response(enrollment_json(enrollment), status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_my_courses(request):
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    return Response([enrollment_json(e) for e in enrollments])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_materials(request):
    course_ids = Enrollment.objects.filter(student=request.user).values_list('course_id', flat=True)
    items = Material.objects.filter(course_id__in=course_ids).select_related('course')
    return Response([{
        'id': m.id,
        'title': m.title,
        'material_type': m.material_type,
        'file': m.file.url if m.file else None,
        'external_url': m.external_url,
        'course': m.course.title,
    } for m in items])


def _get_enrollment_for_lesson(request, lesson):
    return Enrollment.objects.filter(student=request.user, course=lesson.module.course).first()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    enrollment = _get_enrollment_for_lesson(request, lesson)
    if enrollment is None:
        return Response({'detail': 'Enroll in this course to access its lessons.'}, status=403)

    completed = LessonProgress.objects.filter(enrollment=enrollment, lesson=lesson).exists()
    return Response({
        'id': lesson.id,
        'title': lesson.title,
        'order': lesson.order,
        'video_url': lesson.video_url,
        'pdf': lesson.pdf.url if lesson.pdf else None,
        'content': lesson.content,
        'completed': completed,
        'course_slug': lesson.module.course.slug,
        'module_title': lesson.module.title,
        'assignments': [
            {'id': a.id, 'title': a.title, 'points': a.points} for a in lesson.assignments.all()
        ],
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_mark_complete(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    enrollment = _get_enrollment_for_lesson(request, lesson)
    if enrollment is None:
        return Response({'detail': 'Enroll in this course to access its lessons.'}, status=403)

    LessonProgress.objects.get_or_create(enrollment=enrollment, lesson=lesson)
    return Response({'completed': True})
