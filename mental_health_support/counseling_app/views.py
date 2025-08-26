from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Profile, ClientProfile, CounselorApplication, Session
from .serializers import ProfileSerializer, ClientProfileSerializer, CounselorApplicationSerializer, SessionSerializer


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










# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def hello_world(request):
#     return Response({"message": f"Hello, {request.user.username}!"})
