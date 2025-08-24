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
    














# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def hello_world(request):
#     return Response({"message": f"Hello, {request.user.username}!"})
