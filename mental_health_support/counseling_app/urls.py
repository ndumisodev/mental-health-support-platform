from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet, ClientProfileViewSet, CounselorApplicationViewSet

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'client-profiles', ClientProfileViewSet, basename='client-profile')
router.register(r'counselor-applications', CounselorApplicationViewSet, basename='counselor-application')

urlpatterns = [
    path('', include(router.urls)),
]
