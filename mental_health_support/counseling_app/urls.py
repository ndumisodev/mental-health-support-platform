from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet, AvailabilityListView, ClientProfileViewSet, CounselorApplicationViewSet,SessionViewSet, ReviewViewSet, MessageViewSet, EmergencyRequestViewSet,AuditLogViewSet

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'client-profiles', ClientProfileViewSet, basename='client-profile')
router.register(r'counselor-applications', CounselorApplicationViewSet, basename='counselor-application')
router.register(r'sessions', SessionViewSet, basename='session')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'emergencies', EmergencyRequestViewSet, basename='emergency')
router.register(r'audit/logs', AuditLogViewSet, basename='audit-log')


urlpatterns = [
    path('', include(router.urls)),

    # Chat messages nested under session_id
    path('chat/<int:session_id>/messages/', 
         MessageViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='chat-messages'),
    path('availability/', AvailabilityListView.as_view(), name='availability-list'),
]
