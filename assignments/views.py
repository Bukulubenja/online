from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

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


@login_required(login_url='login')
def assignment_list(request):
    course_ids = Enrollment.objects.filter(student=request.user).values_list('course_id', flat=True)
    assignments = Assignment.objects.filter(
        lesson__module__course_id__in=course_ids
    ).select_related('lesson__module__course')

    submissions = {
        s.assignment_id: s
        for s in Submission.objects.filter(student=request.user, assignment__in=assignments)
    }

    rows = []
    for assignment in assignments:
        submission = submissions.get(assignment.id)
        rows.append({
            'assignment': assignment,
            'submission': submission,
            'status': _status_for(assignment, submission),
        })

    return render(request, 'assignments.html', {'rows': rows})


def _get_enrollment(request, assignment):
    return Enrollment.objects.filter(
        student=request.user, course=assignment.lesson.module.course
    ).first()


@login_required(login_url='login')
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    enrollment = _get_enrollment(request, assignment)

    if enrollment is None:
        messages.error(request, 'Enroll in this course to access its assignments.')
        return redirect('course_detail', slug=assignment.lesson.module.course.slug)

    submission = Submission.objects.filter(assignment=assignment, student=request.user).first()
    return render(request, 'assignment_detail.html', {
        'assignment': assignment,
        'submission': submission,
        'status': _status_for(assignment, submission),
    })


@login_required(login_url='login')
@require_POST
def submit_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    enrollment = _get_enrollment(request, assignment)

    if enrollment is None:
        messages.error(request, 'Enroll in this course to access its assignments.')
        return redirect('course_detail', slug=assignment.lesson.module.course.slug)

    content = request.POST.get('content', '').strip()
    file = request.FILES.get('file')

    if not content and not file:
        messages.error(request, 'Write a response or attach a file before submitting.')
        return redirect('assignment_detail', pk=pk)

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

    messages.success(request, 'Assignment submitted.')
    return redirect('assignment_detail', pk=pk)
