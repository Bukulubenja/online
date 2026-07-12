from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from courses.models import Course, Lesson

from .models import Enrollment, LessonProgress


@login_required(login_url='login')
@require_POST
def enroll(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)

    if course.price > 0:
        messages.error(request, 'Payment coming soon for this course.')
        return redirect('course_detail', slug=slug)

    Enrollment.objects.get_or_create(student=request.user, course=course)
    return redirect('course_detail', slug=slug)


@login_required(login_url='login')
def my_courses(request):
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    return render(request, 'my_courses.html', {'enrollments': enrollments})


def _get_enrollment_for_lesson(request, lesson):
    return Enrollment.objects.filter(
        student=request.user, course=lesson.module.course
    ).first()


@login_required(login_url='login')
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    enrollment = _get_enrollment_for_lesson(request, lesson)

    if enrollment is None:
        messages.error(request, 'Enroll in this course to access its lessons.')
        return redirect('course_detail', slug=lesson.module.course.slug)

    completed = LessonProgress.objects.filter(enrollment=enrollment, lesson=lesson).exists()
    return render(request, 'lesson_detail.html', {
        'lesson': lesson,
        'completed': completed,
    })


@login_required(login_url='login')
@require_POST
def mark_complete(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    enrollment = _get_enrollment_for_lesson(request, lesson)

    if enrollment is None:
        messages.error(request, 'Enroll in this course to access its lessons.')
        return redirect('course_detail', slug=lesson.module.course.slug)

    LessonProgress.objects.get_or_create(enrollment=enrollment, lesson=lesson)
    return redirect('lesson_detail', lesson_id=lesson.id)
