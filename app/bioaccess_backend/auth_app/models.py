import os
import uuid
import qrcode
from io import BytesIO
from django.core.files import File
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django_cryptography.fields import encrypt

# ---------------------------------------------------------------------
# RoomGroup Model
# ---------------------------------------------------------------------
class RoomGroup(models.Model):
    """
    Represents a group of rooms (access points). This allows the system to manage permissions in bulk.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

# ---------------------------------------------------------------------
# CustomUser Model
# ---------------------------------------------------------------------
class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Additional fields:
      - is_admin: Indicates if the user is an administrator.
      - is_approved: Indicates if the user’s registration has been reviewed and approved by an admin.
      - allowed_room_groups: Groups of rooms this user is allowed to access.
      - face_reference_image: Encrypted stored reference image for facial recognition.
      - voice_reference: Encrypted stored reference voice sample for speaker verification.
    """
    is_admin = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False, help_text="Set to True once admin approves registration.")
    allowed_room_groups = models.ManyToManyField(RoomGroup, blank=True)
    face_reference_image = encrypt(models.ImageField(upload_to="faces/", null=True, blank=True))
    voice_reference = encrypt(models.FileField(upload_to="voices/", null=True, blank=True))
    
    # Override the related names for groups and permissions to avoid reverse accessor clashes.
    groups = models.ManyToManyField(
        Group,
        related_name="custom_users",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_users",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )
    
    def __str__(self):
        return self.username

# ---------------------------------------------------------------------
# Room Model
# ---------------------------------------------------------------------
class Room(models.Model):
    """
    Represents an access point (physical door or checkpoint).
    Each room is assigned a unique room_id (auto-generated if not provided) and a dynamic QR code.
    The room is associated with a RoomGroup for permission management.
    """
    name = models.CharField(max_length=100)
    room_id = models.CharField(max_length=50, unique=True, blank=True)
    qr_code = models.ImageField(upload_to="qrcodes/", blank=True, editable=False)
    group = models.ForeignKey(RoomGroup, on_delete=models.CASCADE, related_name="rooms", null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.room_id:
            self.room_id = str(uuid.uuid4())[:8]
        # Generate a QR code image from the room_id.
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.room_id)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        filename = f"{self.room_id}.png"
        self.qr_code.save(filename, File(buffer), save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.room_id})"

# ---------------------------------------------------------------------
# AccessLog Model
# ---------------------------------------------------------------------
class AccessLog(models.Model):
    """
    Logs successful authentication attempts.
    Fields:
      - user: The authenticated user.
      - room: The room where access was granted.
      - timestamp: Auto-generated timestamp of the event.
      - remarks: Encrypted remarks or details (e.g., similarity scores, model outputs).
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    remarks = encrypt(models.TextField(blank=True, null=True))
    
    def __str__(self):
        return f"Access Granted: {self.user.username} - {self.room.name} @ {self.timestamp}"

# ---------------------------------------------------------------------
# DeniedLog Model
# ---------------------------------------------------------------------
class DeniedLog(models.Model):
    """
    Logs failed authentication attempts.
    Fields:
      - user: The user who attempted authentication.
      - room: The room at which the attempt was made.
      - timestamp: Auto-generated timestamp.
      - reason: Encrypted reason for denial (e.g., "Face verification failed", "Liveness check failed").
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    reason = encrypt(models.TextField(blank=True, null=True))
    
    def __str__(self):
        return f"Access Denied: {self.user.username} - {self.room.name} @ {self.timestamp} (Reason: {self.reason})"
