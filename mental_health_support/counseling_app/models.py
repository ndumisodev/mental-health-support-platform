from django.db import models
from django.contrib.auth.models import User


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



class CounselorProfile(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=255)
    availability = models.JSONField()
    certifications = models.TextField(blank=True)
    experience = models.PositiveIntegerField(help_text="Years of experience")

    def __str__(self):
        return f"Counselor Profile for {self.profile.user.username}"


class ClientProfile(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=50)
    preferences = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Client Profile for {self.profile.user.username}"


