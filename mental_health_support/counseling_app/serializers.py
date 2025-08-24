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


