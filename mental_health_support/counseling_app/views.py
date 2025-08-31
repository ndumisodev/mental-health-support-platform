from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import AuditLog, Profile, ClientProfile, CounselorApplication, Session, Review, ChatRoom, Message, EmergencyRequest, Availability
from .serializers import ProfileSerializer, ClientProfileSerializer, CounselorApplicationSerializer, SessionSerializer, ReviewSerializer, MessageSerializer, EmergencyRequestSerializer, AuditLogSerializer, AvailabilitySerializer
from rest_framework import generics
from rest_framework.response import Response


class ProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user profiles (both clients and counselors).

    - list: List all profiles (filterable by role)
    - retrieve: Get a specific profile
    - create: Create a profile for the logged-in user
    - update/partial_update: Update own profile
    """

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """Assign the logged-in user as the owner of the profile."""
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """Optionally filter profiles by role."""
        role = self.request.query_params.get('role')
        if role:
            return self.queryset.filter(role=role)
        return self.queryset
    
    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """
        Returns a list of available datetime slots for a given counselor.
        Only future times are returned, and already booked sessions are excluded.
        """
        counselor = self.get_object()
        if counselor.role != Profile.ROLE_COUNSELOR:
            return Response({"error": "Profile is not a counselor"}, status=status.HTTP_400_BAD_REQUEST)

        availabilities = Availability.objects.filter(counselor=counselor)
        now = timezone.now()
        slots = []

        # Generate slots for the next 7 days
        for avail in availabilities:
            for i in range(7):
                date = now.date() + timedelta(days=i)
                if date.weekday() == avail.day_of_week:
                    start_dt = datetime.combine(date, avail.start_time)
                    end_dt = datetime.combine(date, avail.end_time)

                    current = timezone.make_aware(start_dt)
                    while current < timezone.make_aware(end_dt):
                        # Exclude already booked sessions
                        is_booked = Session.objects.filter(
                            counselor=counselor,
                            datetime=current,
                            status__in=[Session.STATUS_PENDING, Session.STATUS_CONFIRMED]
                        ).exists()
                        if not is_booked and current > now:
                            slots.append(current)

                        current += timedelta(hours=1)

        return Response({"available_slots": slots})
    


class ClientProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing client-specific profile data.

    - retrieve: View client profile details
    - create: Create client profile linked to a Profile
    - update/partial_update: Update client-specific details
    """

    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Ensure user is a client and has a ClientProfile
        return ClientProfile.objects.get(profile__user=self.request.user)


class CounselorApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for counselor applications.

    - list: View all counselor applications (admin only)
    - retrieve: View a specific application
    - create: Submit an application to become a counselor
    """

    queryset = CounselorApplication.objects.all()
    serializer_class = CounselorApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Restrict list view to admin users."""
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(profile__user=self.request.user)
    
    def get_object(self):
        # Ensure user is a counselor and has a CounselorProfile
        return CounselorApplication.objects.get(profile__user=self.request.user)
    

class SessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing counseling session bookings.

    Endpoints:
        - POST /sessions/:
            Create a new session booking. Automatically associates the
            authenticated client with the booking.
        - GET /sessions/{id}/:
            Retrieve details for a specific session.
        - PATCH /sessions/{id}/status/:
            Update the status of a session (pending, confirmed, completed).

    Permissions:
        - Only authenticated users can access this endpoint.

    Attributes:
        queryset (QuerySet): All session records.
        serializer_class (Serializer): SessionSerializer for validation and data handling.
        permission_classes (list): Restricts access to authenticated users only.
    """
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Automatically assign the logged-in user as the client for new sessions.
        """
        client_profile = self.request.user.profile
        if client_profile.role != Profile.ROLE_CLIENT:
            raise PermissionError("Only clients can create sessions.")
        serializer.save(client=client_profile)

    @action(detail=True, methods=['patch'])
    def status(self, request, pk=None):
        """
        Allows a counselor or admin to change the status of a booking.

        Example request body: { "status": "confirmed" }
        """
        session = self.get_object()
        new_status = request.data.get("status")

        if new_status not in [
            Session.STATUS_PENDING,
            Session.STATUS_CONFIRMED,
            Session.STATUS_COMPLETED,
            Session.STATUS_CANCELLED
        ]:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        session.status = new_status
        session.save()
        return Response({"status": session.status})



class IsReviewerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only the reviewer to edit/delete their review.
    Others can only read.
    """
    def has_object_permission(self, request, view, obj):
        # Safe methods like GET are always allowed
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only reviewer can modify
        return obj.reviewer == request.user

class ReviewViewSet(viewsets.ModelViewSet):
    """
    API endpoint for creating, viewing, and editing reviews.
    """
    queryset = Review.objects.all().select_related('session', 'counselor', 'reviewer')
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsReviewerOrReadOnly]

    def get_queryset(self):
        """
        Limit reviews returned:
        - Counselors see reviews about them
        - Clients see reviews they wrote
        - Admin sees all reviews
        """
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(
            reviewer=user
        ) | self.queryset.filter(
            counselor=user
        )

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        session_id = self.kwargs['session_id']
        session = get_object_or_404(Session, pk=session_id)

        # Ensure only participants can view messages
        if self.request.user.profile not in [session.client, session.counselor]:
            return Message.objects.none()

        room, _ = ChatRoom.objects.get_or_create(session=session)
        return Message.objects.filter(room=room).order_by('created_at')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['session_id'] = self.kwargs['session_id']
        return context


class EmergencyRequestViewSet(viewsets.ModelViewSet):
    queryset = EmergencyRequest.objects.all().select_related('user')
    serializer_class = EmergencyRequestSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            # Only staff can view emergencies
            permission_classes = [permissions.IsAdminUser]
        else:
            # Clients can create emergencies
            permission_classes = [permissions.IsAuthenticated]
        return [perm() for perm in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset.order_by('-created_at')
        # Clients cannot view others' emergencies
        return EmergencyRequest.objects.none()



class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin-only endpoint for viewing audit logs.
    """
    queryset = AuditLog.objects.all().select_related('user')
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]


class AvailabilityListView(generics.ListAPIView):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer

