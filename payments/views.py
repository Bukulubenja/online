import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from courses.models import Course
from enrollments.models import Enrollment

from .models import METHOD_CHOICES, Payment


@login_required(login_url='login')
def checkout(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)

    if course.price <= 0:
        return redirect('course_detail', slug=slug)

    if Enrollment.objects.filter(student=request.user, course=course).exists():
        return redirect('course_detail', slug=slug)

    if request.method == 'POST':
        method = request.POST.get('method')
        if method not in dict(METHOD_CHOICES):
            messages.error(request, 'Please choose a payment method.')
            return render(request, 'checkout.html', {'course': course, 'methods': METHOD_CHOICES})

        payment = Payment.objects.create(
            student=request.user,
            course=course,
            amount=course.price,
            method=method,
            status='pending',
        )
        return redirect('confirm_payment', payment_id=payment.id)

    return render(request, 'checkout.html', {'course': course, 'methods': METHOD_CHOICES})


@login_required(login_url='login')
def confirm_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, student=request.user)

    if payment.status == 'pending':
        payment.status = 'success'
        payment.transaction_id = f'MOCK-{uuid.uuid4().hex[:12].upper()}'
        payment.save()
        Enrollment.objects.get_or_create(student=request.user, course=payment.course)

    return redirect('receipt', payment_id=payment.id)


@login_required(login_url='login')
def receipt(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, student=request.user)
    return render(request, 'receipt.html', {'payment': payment})
