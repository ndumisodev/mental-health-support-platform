from django.contrib import admin
from .models import Profile, ClientProfile, CounselorApplication, Availability


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

@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('counselor', 'day_of_week', 'start_time', 'end_time')
    list_filter = ('day_of_week', 'counselor')


from django.contrib import admin
from .models import Session

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'counselor', 'datetime', 'status')
    list_filter = ('status', 'datetime', 'counselor')
    search_fields = ('client__user__username', 'counselor__user__username')
    ordering = ('-datetime',)
