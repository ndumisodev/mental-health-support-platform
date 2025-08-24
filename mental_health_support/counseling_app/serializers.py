from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, CounselorApplication, ClientProfile

class UserSerializer(serializers.ModelSerializer):
    """UserSerializer so that we can nest basic user details inside other serializers."""
    
    class Meta:
        model = User
        field = ["id", "username", "email", "first_name", "last_name"]

class ProfileSerializer(serializers.ModelSerializer):
    """ """

    user = UserSerializer(read_only=True)   #Nested read only field, so we can user Info

    class Meta:
        model = Profile
        fields = ["id", "user", "role", "bio", "profile_pictuer"]


class ClientProfileSerializer(serializers.ModelSerializer):
    """ """

    profile = ProfileSerializer(read_only=True)
    profile_id = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.all(),
        source="profile",
        write_only=True
    )

    class Meta:
        model = ClientProfile
        fields = ["id", "profile", "profile_id", "age", "gender", "preferences"]



class CounselorApplicationSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)  # Show profile details, not editable
    profile_id = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.all(),
        source="profile",
        write_only=True
    )

    class Meta:
        model = CounselorApplication
        fields = [
            "id",
            "profile",       # Read-only detailed profile
            "profile_id",    # Write-only ID for linking
            "status",
            "specialization",
            "experience_years",
            "certifications",
            "submitted_at"
        ]
        read_only_fields = ["status", "submitted_at"]