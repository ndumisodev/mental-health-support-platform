from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, CounselorApplication, ClientProfile

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for Django's built-in User model.

    This serializer exposes basic user details and is primarily used for
    nesting within other serializers, so related objects can display 
    user information without requiring separate API calls.
    """
    
    class Meta:
        model = User
        field = ["id", "username", "email", "first_name", "last_name"]

class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the Profile model.

    Provides general profile information for both clients and counselors,
    including role, bio, and profile picture.
    The related User details are nested as read-only.
    """

    user = UserSerializer(read_only=True)   #Nested read only field, so we can user Info

    class Meta:
        model = Profile
        fields = ["id", "user", "role", "bio", "profile_picture"]


class ClientProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the ClientProfile model.

    Represents client-specific information such as age, gender,
    and preferences, linked to a base Profile object.
    
    Includes:
    - profile: Nested read-only Profile data
    - profile_id: Write-only field for linking to an existing Profile
    """

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
    """
    Serializer for the CounselorApplication model.

    Used when a user applies to be a counselor.
    Links to a base Profile object and stores counselor-specific
    details such as specialization, experience years, and certifications.

    - profile: Read-only nested Profile details
    - profile_id: Write-only field for linking to an existing Profile
    - status: Application status (read-only)
    - submitted_at: Timestamp when application was submitted (read-only)
    """

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
            "availability",
            "certifications",
            "submitted_at"
        ]
        read_only_fields = ["status", "submitted_at"]