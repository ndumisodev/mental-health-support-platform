from django.contrib import admin
from .models import Profile, ClientProfile, CounselorApplication

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'bio')

@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('profile', 'age', 'gender')

@admin.register(CounselorApplication)
class CounselorApplicationAdmin(admin.ModelAdmin):
    list_display = ('profile', 'status', 'specialization', 'experience_years', 'submitted_at')
    list_filter = ('status',)

