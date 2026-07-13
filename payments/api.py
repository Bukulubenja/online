import uuid

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from courses.models import Course
from enrollments.models import Enrollment

from .models import METHOD_CHOICES, Payment


def payment_json(payment):
    return {
        'id': payment.id,
        'course': payment.course.title,
        'amount': str(payment.amount),
        'method': payment.method,
        'status': payment.status,
        'transaction_id': payment.transaction_id,
        'created_at': payment.created_at,
    }


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_checkout(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)

    if course.price <= 0:
        return Response({'detail': 'This course is free — enroll directly.'}, status=400)

    if Enrollment.objects.filter(student=request.user, course=course).exists():
        return Response({'detail': 'Already enrolled.'}, status=400)

    method = request.data.get('method')
    if method not in dict(METHOD_CHOICES):
        return Response({'detail': 'Please choose a valid payment method.'}, status=400)

    payment = Payment.objects.create(
        student=request.user, course=course, amount=course.price, method=method, status='pending',
    )
    return Response(payment_json(payment), status=201)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_confirm_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, student=request.user)

    if payment.status == 'pending':
        payment.status = 'success'
        payment.transaction_id = f'MOCK-{uuid.uuid4().hex[:12].upper()}'
        payment.save()
        Enrollment.objects.get_or_create(student=request.user, course=payment.course)

    return Response(payment_json(payment))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_receipt(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, student=request.user)
    return Response(payment_json(payment))
