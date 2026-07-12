from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render

from enrollments.models import LessonProgress
from .models import User


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        current_level = request.POST.get('current_level', '').strip()
        password = request.POST.get('password', '')

        form_data = {
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'current_level': current_level,
        }

        if not email or not password:
            messages.error(request, 'Email and password are required.')
            return render(request, 'signup.html', form_data)

        if User.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists.')
            return render(request, 'signup.html', form_data)

        try:
            validate_password(password)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return render(request, 'signup.html', form_data)

        username = email.split('@')[0]
        base_username = username
        suffix = 1
        while User.objects.filter(username=username).exists():
            username = f'{base_username}{suffix}'
            suffix += 1

        first_name = full_name.split(' ')[0] if full_name else ''
        last_name = ' '.join(full_name.split(' ')[1:]) if full_name else ''

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            current_level=current_level,
        )
        user.backend = 'user.backends.EmailOrUsernameBackend'
        auth_login(request, user)
        return redirect('dashboard')

    return render(request, 'signup.html')


def logout(request):
    auth_logout(request)
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    enrollments = list(request.user.enrollments.select_related('course').order_by('-enrolled_at'))
    completed_lessons = LessonProgress.objects.filter(enrollment__student=request.user).count()
    certificates_count = request.user.certificates.filter(is_valid=True).count()
    avg_progress = round(sum(e.progress_percent for e in enrollments) / len(enrollments)) if enrollments else 0
    continue_enrollment = next((e for e in enrollments if e.progress_percent < 100), None)
    return render(request, 'dashboard.html', {
        'enrollments': enrollments,
        'completed_lessons': completed_lessons,
        'certificates_count': certificates_count,
        'avg_progress': avg_progress,
        'continue_enrollment': continue_enrollment,
    })
