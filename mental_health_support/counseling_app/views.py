from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Profile, ClientProfile, CounselorApplication
from .serializers import ProfileSerializer, ClientProfileSerializer, CounselorApplicationSerializer


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









# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def hello_world(request):
#     return Response({"message": f"Hello, {request.user.username}!"})
