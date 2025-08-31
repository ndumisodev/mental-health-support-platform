from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings


class Profile(models.Model):
    ROLE_CLIENT = "client"
    ROLE_COUNSELOR = "counselor"

    ROLE_CHOICES = [
        (ROLE_CLIENT, 'Client'),
        (ROLE_COUNSELOR, 'Counselor'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CLIENT)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to="profiles/", null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role.capitalize()}"


class CounselorApplication(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    specialization = models.CharField(max_length=255)
    experience_years = models.IntegerField()
    availability = models.JSONField(default=dict)
    certifications = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Application from {self.profile.user.username} - {self.status}"


class ClientProfile(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=50)
    preferences = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Client Profile for {self.profile.user.username}"


class Availability(models.Model):
    counselor = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        limit_choices_to={'role': Profile.ROLE_COUNSELOR},
        related_name="availabilities"
    )
    day_of_week = models.IntegerField(
        choices=[
            (0, "Monday"),
            (1, "Tuesday"),
            (2, "Wednesday"),
            (3, "Thursday"),
            (4, "Friday"),
            (5, "Saturday"),
            (6, "Sunday"),
        ]
    )
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.counselor.user.username} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class Session(models.Model):
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    counselor = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        limit_choices_to={'role': Profile.ROLE_COUNSELOR},
        related_name="sessions_as_counselor"
    )
    client = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        limit_choices_to={'role': Profile.ROLE_CLIENT},
        related_name="sessions_as_client"
    )
    datetime = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.client.user.username} with {self.counselor.user.username} at {self.datetime}"


class Review(models.Model):
    session = models.OneToOneField(
        'Session',
        on_delete=models.CASCADE,
        related_name='review'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_given'
    )
    counselor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_received'
    )
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(rating__gte=1, rating__lte=5),
                name='rating_between_1_and_5'
            )
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reviewer} → {self.counselor} ({self.rating}⭐)"



class ChatRoom(models.Model):
    session = models.OneToOneField(
        Session,
        on_delete=models.CASCADE,
        related_name='chat_room'
    )

    def __str__(self):
        return f"ChatRoom for Session {self.session.id}"


class Message(models.Model):
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        Profile,  # Uses Profile since that's store client/counselor info
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.user.username} in Room {self.room.id}"


class EmergencyRequest(models.Model):
    STATUS_PENDING = "pending"
    STATUS_RESOLVED = "resolved"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_RESOLVED, "Resolved"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="emergency_requests"
    )
    details = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    hotline_info = models.JSONField(null=True, blank=True)  # Stores SADAG hotline info
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Emergency from {self.user.username} ({self.status})"
    

class AuditLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="audit_logs"
    )
    action = models.CharField(max_length=255)
    entity = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} | {self.action} | {self.entity} | {self.timestamp}"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)  # client is default
    else:
        instance.profile.save()



@receiver(post_save, sender=CounselorApplication)
def update_profile_role_on_approval(sender, instance, **kwargs):
    """
    Automatically update the Profile role to 'counselor'
    when a counselor application is approved.
    """
    if instance.status == CounselorApplication.STATUS_APPROVED:
        profile = instance.profile
        if profile.role != Profile.ROLE_COUNSELOR:
            profile.role = Profile.ROLE_COUNSELOR
            profile.save()



@receiver(post_save, sender=CounselorApplication)
def update_profile_role_on_approval(sender, instance, **kwargs):
    """
    Automatically update the Profile role to 'counselor'
    and send a notification email.
    """
    profile = instance.profile
    user = profile.user

    if instance.status == CounselorApplication.STATUS_APPROVED:
        if profile.role != Profile.ROLE_COUNSELOR:
            profile.role = Profile.ROLE_COUNSELOR
            profile.save()
        
        # Send approval email
        send_mail(
            subject="Your Counselor Application has been Approved",
            message="Congratulations! Your counselor application has been approved. You can now log in as a counselor.",
            from_email="admin@yourdomain.com",
            recipient_list=[user.email],
            fail_silently=False,
        )

    elif instance.status == CounselorApplication.STATUS_REJECTED:
        # Send rejection email
        send_mail(
            subject="Your Counselor Application has been Rejected",
            message="Unfortunately, your counselor application has been rejected. Please contact support for more information.",
            from_email="admin@yourdomain.com",
            recipient_list=[user.email],
            fail_silently=False,
        )