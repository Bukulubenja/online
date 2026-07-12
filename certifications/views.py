from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from enrollments.models import Enrollment

from .models import Certificate, Exam, ExamAttempt, ExamAnswer


def _is_eligible(user, level):
    if Certificate.objects.filter(student=user, exam__level=level, is_valid=True).exists():
        return False
    for enrollment in Enrollment.objects.filter(student=user, course__level=level):
        if enrollment.progress_percent == 100:
            return True
    return False


def exam_list(request):
    exams = Exam.objects.filter(is_published=True)
    return render(request, 'certifications.html', {'exams': exams})


def exam_detail(request, level):
    exam = get_object_or_404(Exam, level=level, is_published=True)
    return render(request, 'certification_detail.html', {'exam': exam})


def certificate_verify(request, certificate_id):
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id)
    return render(request, 'certificate_verify.html', {'certificate': certificate})


@login_required(login_url='login')
def my_exams(request):
    exams = Exam.objects.filter(is_published=True)
    attempts = {a.exam_id: a for a in ExamAttempt.objects.filter(student=request.user)}
    rows = []
    for exam in exams:
        rows.append({
            'exam': exam,
            'attempt': attempts.get(exam.id),
            'eligible': _is_eligible(request.user, exam.level),
        })
    return render(request, 'my_exams.html', {'rows': rows})


@login_required(login_url='login')
@require_POST
def register_exam(request, level):
    exam = get_object_or_404(Exam, level=level, is_published=True)

    existing = ExamAttempt.objects.filter(student=request.user, exam=exam, submitted_at__isnull=True).first()
    if existing:
        return redirect('take_exam', attempt_id=existing.id)

    if not _is_eligible(request.user, level):
        messages.error(request, 'Complete a course at this level before registering for the exam.')
        return redirect('my_exams')

    attempt = ExamAttempt.objects.create(student=request.user, exam=exam, fee_paid=True)
    return redirect('take_exam', attempt_id=attempt.id)


@login_required(login_url='login')
def take_exam(request, attempt_id):
    attempt = get_object_or_404(ExamAttempt, id=attempt_id, student=request.user)
    if attempt.submitted_at is not None:
        return redirect('exam_result', attempt_id=attempt.id)

    questions = attempt.exam.questions.prefetch_related('choices')
    return render(request, 'take_exam.html', {'attempt': attempt, 'questions': questions})


@login_required(login_url='login')
@require_POST
def submit_exam(request, attempt_id):
    attempt = get_object_or_404(ExamAttempt, id=attempt_id, student=request.user)
    if attempt.submitted_at is not None:
        return redirect('exam_result', attempt_id=attempt.id)

    questions = list(attempt.exam.questions.prefetch_related('choices'))
    correct_count = 0
    for question in questions:
        choice_id = request.POST.get(f'question_{question.id}')
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

    return redirect('exam_result', attempt_id=attempt.id)


@login_required(login_url='login')
def exam_result(request, attempt_id):
    attempt = get_object_or_404(ExamAttempt, id=attempt_id, student=request.user)
    certificate = None
    if attempt.passed:
        certificate = Certificate.objects.filter(student=request.user, exam=attempt.exam).first()
    return render(request, 'exam_result.html', {'attempt': attempt, 'certificate': certificate})


@login_required(login_url='login')
def my_certificates(request):
    certificates = Certificate.objects.filter(student=request.user).select_related('exam')
    return render(request, 'my_certificates.html', {'certificates': certificates})
