from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, CounselorApplication, ClientProfile, Session, Availability, Profile
from django.utils import timezone


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for Django's built-in User model.

    This serializer exposes basic user details and is primarily used for
    nesting within other serializers, so related objects can display 
    user information without requiring separate API calls.
    """
    
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]

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


class SessionSerializer(serializers.ModelSerializer):
    """
    Serializer for handling session booking between clients and counselors.

    Validations performed:
    1. The requested datetime must be in the future.
    2. The requested datetime must match the counselor's availability schedule.
    3. Prevents double booking by checking for existing pending or confirmed sessions
       at the same time for the same counselor.

    Fields:
        counselor (ForeignKey): The counselor being booked.
        client (ForeignKey): The client making the booking.
        datetime (DateTimeField): The scheduled date and time of the session.
        status (CharField): The current status of the session (pending, confirmed, completed).
    """
    class Meta:
        model = Session
        fields = "__all__"

    def validate(self, data):
        """
        Custom validation for booking rules.

        Raises:
            serializers.ValidationError: If:
                - The booking date is in the past.
                - The counselor is not available at the requested time.
                - The time slot is already booked.
        
        Returns:
            dict: The validated booking data.
        """
        requested_datetime = data['datetime']
        counselor = data["counselor"]

        # Date must be in the future
        if requested_datetime <= timezone.now():
            raise serializers.ValidationError("You cannot book a date from the past")
    
        # Date must match counselor availability
        day_of_week = requested_datetime.weekday()  # Monday=0, Sunday=6
        time_only = requested_datetime.time()

        availability_exists = Availability.objects.filter(
            counselor=counselor,
            day_of_week=day_of_week,
            start_time__lte=time_only,
            end_time__gt=time_only
        ).exists()

        if not availability_exists:
            raise serializers.ValidationError("This counselor is not available at this time.")
        
        # Preventing double booking
        clash_exists = Session.objects.filter(
            counselor=counselor,
            datetime=requested_datetime,
            status__in=[Session.STATUS_PENDING, Session.STATUS_CONFIRMED]
        ).exists()

        if clash_exists:
            raise serializers.ValidationError("This time slot is already booked.")
        
        return data


from rest_framework import serializers
from .models import Review, Session

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            'id',
            'session',
            'reviewer',
            'counselor',
            'rating',
            'comment',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'reviewer']

    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user
        session = attrs.get('session')

        #Ensure session exists
        if not session:
            raise serializers.ValidationError("Session is required.")

        #Check session is completed
        if session.status != 'completed':
            raise serializers.ValidationError("You can only review a completed session.")

        #Reviewer must be the session's client
        if session.client != user:
            raise serializers.ValidationError("You can only review sessions you attended as a client.")

        #Counselor in review must match session's counselor
        if attrs.get('counselor') != session.counselor:
            raise serializers.ValidationError("Counselor does not match the session's counselor.")

        #Checking if a review already exists for this session
        if Review.objects.filter(session=session).exists():
            raise serializers.ValidationError("This session already has a review.")

        return attrs

    def create(self, validated_data):
        validated_data['reviewer'] = self.context['request'].user
        return super().create(validated_data)