from django.shortcuts import get_object_or_404, render
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Course
from .serializers import CourseSerializer


class CourseViewSet(ReadOnlyModelViewSet):
    queryset = Course.objects.filter(is_published=True)
    serializer_class = CourseSerializer
    lookup_field = 'slug'


def course_list(request):
    courses = Course.objects.filter(is_published=True)
    return render(request, 'courses.html', {'courses': courses})


def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    return render(request, 'course_detail.html', {'course': course})
