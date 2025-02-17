from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Room, AccessLog, DeniedLog, RoomGroup

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'is_admin', 'is_approved')
    list_filter = ('is_admin', 'allowed_room_groups')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'face_reference_image', 'voice_reference')}),
        ('Permissions', {'fields': ('is_admin', 'is_active', 'groups', 'user_permissions', 'allowed_room_groups')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'face_reference_image', 'voice_reference', 'password1', 'password2', 'is_admin'),
        }),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'room_id', 'qr_code')
    readonly_fields = ('qr_code',)

@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'timestamp', 'remarks')
    list_filter = ('timestamp',)
    search_fields = ('user__username', 'room__name')

@admin.register(DeniedLog)
class DeniedLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'timestamp', 'reason')
    list_filter = ('timestamp',)
    search_fields = ('user__username', 'room__name')

@admin.register(RoomGroup)
class RoomGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
