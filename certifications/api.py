from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from enrollments.models import Enrollment

from .models import Certificate, Exam, ExamAnswer, ExamAttempt


def _is_eligible(user, level):
    if Certificate.objects.filter(student=user, exam__level=level, is_valid=True).exists():
        return False
    for enrollment in Enrollment.objects.filter(student=user, course__level=level):
        if enrollment.progress_percent == 100:
            return True
    return False


def exam_json(exam):
    return {
        'level': exam.level,
        'title': exam.title,
        'duration_minutes': exam.duration_minutes,
        'passing_score': exam.passing_score,
        'fee': str(exam.fee),
    }


@api_view(['GET'])
@permission_classes([AllowAny])
def api_exam_list(request):
    exams = Exam.objects.filter(is_published=True)
    return Response([exam_json(e) for e in exams])


@api_view(['GET'])
@permission_classes([AllowAny])
def api_certificate_verify(request, certificate_id):
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id)
    return Response({
        'certificate_id': certificate.certificate_id,
        'student': certificate.student.get_full_name() or certificate.student.username,
        'exam_level': certificate.exam.level,
        'exam_title': certificate.exam.title,
        'issued_at': certificate.issued_at,
        'is_valid': certificate.is_valid,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_my_exams(request):
    exams = Exam.objects.filter(is_published=True)
    attempts = {}
    for attempt in ExamAttempt.objects.filter(student=request.user).order_by('id'):
        attempts[attempt.exam_id] = attempt

    rows = []
    for exam in exams:
        attempt = attempts.get(exam.id)
        eligible = _is_eligible(request.user, exam.level)
        can_retake = bool(
            attempt and attempt.submitted_at is not None and not attempt.passed and eligible
        )
        rows.append({
            'exam': exam_json(exam),
            'attempt': {
                'id': attempt.id,
                'submitted_at': attempt.submitted_at,
                'score': attempt.score,
                'passed': attempt.passed,
            } if attempt else None,
            'eligible': eligible,
            'can_retake': can_retake,
        })
    return Response(rows)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_register_exam(request, level):
    exam = get_object_or_404(Exam, level=level, is_published=True)

    existing = ExamAttempt.objects.filter(student=request.user, exam=exam, submitted_at__isnull=True).first()
    if existing:
        return Response({'attempt_id': existing.id})

    if not _is_eligible(request.user, level):
        return Response({'detail': "Complete a course at this level before registering for the exam."}, status=403)

    attempt = ExamAttempt.objects.create(student=request.user, exam=exam, fee_paid=True)
    return Response({'attempt_id': attempt.id}, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_take_exam(request, attempt_id):
    attempt = get_object_or_404(ExamAttempt, id=attempt_id, student=request.user)
    if attempt.submitted_at is not None:
        return Response({'detail': 'Already submitted.'}, status=400)

    questions = attempt.exam.questions.prefetch_related('choices')
    return Response({
        'attempt_id': attempt.id,
        'exam': exam_json(attempt.exam),
        'questions': [{
            'id': q.id,
            'section': q.section,
            'section_display': q.get_section_display(),
            'text': q.text,
            'choices': [{'id': c.id, 'text': c.text} for c in q.choices.all()],
        } for q in questions],
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_submit_exam(request, attempt_id):
    attempt = get_object_or_404(ExamAttempt, id=attempt_id, student=request.user)
    if attempt.submitted_at is not None:
        return Response({'detail': 'Already submitted.'}, status=400)

    questions = list(attempt.exam.questions.prefetch_related('choices'))
    answers = request.data.get('answers') or {}
    correct_count = 0
    for question in questions:
        choice_id = answers.get(str(question.id))
        selected_choice = None
        if choice_id:
            selected_choice = question.choices.filter(id=choice_id).first()
        ExamAnswer.objects.create(attempt=attempt, question=question, selected_choice=selected_choice)
        if selected_choice is not None and selected_choice.is_correct:
            correct_count += 1

    total = len(questions)
    score = round(correct_count * 100 / total) if total else 0
    passed = score >= attempt.exam.passing_score

    attempt.submitted_at = timezone.now()
    attempt.score = score
    attempt.passed = passed
    attempt.save()

    if passed:
        Certificate.objects.get_or_create(
            student=request.user,
            exam=attempt.exam,
            defaults={'certificate_id': Certificate.generate_id(attempt.exam.level)},
        )

    return Response({'score': score, 'passed': passed, 'attempt_id': attempt.id})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_exam_result(request, attempt_id):
    attempt = get_object_or_404(ExamAttempt, id=attempt_id, student=request.user)
    certificate = None
    if attempt.passed:
        certificate = Certificate.objects.filter(student=request.user, exam=attempt.exam).first()

    return Response({
        'exam': exam_json(attempt.exam),
        'score': attempt.score,
        'passed': attempt.passed,
        'submitted_at': attempt.submitted_at,
        'certificate_id': certificate.certificate_id if certificate else None,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_my_certificates(request):
    certificates = Certificate.objects.filter(student=request.user).select_related('exam')
    return Response([{
        'certificate_id': c.certificate_id,
        'exam_level': c.exam.level,
        'exam_title': c.exam.title,
        'issued_at': c.issued_at,
        'is_valid': c.is_valid,
    } for c in certificates])
