from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from enrollments.models import Enrollment

from .models import Assignment, Submission


def _status_for(assignment, submission):
    if submission and submission.grade is not None:
        return 'graded'
    if submission:
        return 'submitted'
    if assignment.due_at:
        now = timezone.now()
        if assignment.due_at < now:
            return 'overdue'
        if assignment.due_at <= now + timezone.timedelta(days=3):
            return 'due_soon'
    return 'open'


def assignment_json(assignment, submission=None):
    return {
        'id': assignment.id,
        'title': assignment.title,
        'instructions': assignment.instructions,
        'points': assignment.points,
        'due_at': assignment.due_at,
        'course': assignment.lesson.module.course.title,
        'lesson_id': assignment.lesson_id,
        'status': _status_for(assignment, submission),
        'submission': {
            'content': submission.content,
            'file': submission.file.url if submission.file else None,
            'grade': submission.grade,
            'feedback': submission.feedback,
            'submitted_at': submission.submitted_at,
        } if submission else None,
    }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_assignment_list(request):
    course_ids = Enrollment.objects.filter(student=request.user).values_list('course_id', flat=True)
    assignments = Assignment.objects.filter(
        lesson__module__course_id__in=course_ids
    ).select_related('lesson__module__course')

    submissions = {
        s.assignment_id: s
        for s in Submission.objects.filter(student=request.user, assignment__in=assignments)
    }
    return Response([assignment_json(a, submissions.get(a.id)) for a in assignments])


def _get_enrollment(request, assignment):
    return Enrollment.objects.filter(
        student=request.user, course=assignment.lesson.module.course
    ).first()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    enrollment = _get_enrollment(request, assignment)
    if enrollment is None:
        return Response({'detail': 'Enroll in this course to access its assignments.'}, status=403)

    submission = Submission.objects.filter(assignment=assignment, student=request.user).first()
    return Response(assignment_json(assignment, submission))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def api_submit_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    enrollment = _get_enrollment(request, assignment)
    if enrollment is None:
        return Response({'detail': 'Enroll in this course to access its assignments.'}, status=403)

    content = (request.data.get('content') or '').strip()
    file = request.FILES.get('file')

    if not content and not file:
        return Response({'detail': 'Write a response or attach a file before submitting.'}, status=400)

    submission, created = Submission.objects.get_or_create(
        assignment=assignment,
        student=request.user,
        defaults={'content': content, 'file': file},
    )
    if not created:
        submission.content = content
        if file:
            submission.file = file
        submission.grade = None
        submission.feedback = ''
        submission.save()

    return Response(assignment_json(assignment, submission), status=201 if created else 200)
