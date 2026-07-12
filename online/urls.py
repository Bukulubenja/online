
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from courses.views import CourseViewSet

router = DefaultRouter()
router.register('courses', CourseViewSet, basename='course-api')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('web.urls')),
    path('user/', include('user.urls')),
    path('courses/', include('courses.urls')),
    path('portal/', include('enrollments.urls')),
    path('api/', include(router.urls)),

]

urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
