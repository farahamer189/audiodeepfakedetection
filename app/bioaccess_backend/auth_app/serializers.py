from rest_framework import serializers
from .models import CustomUser, Room, AccessLog, DeniedLog, RoomGroup

class RoomGroupSerializer(serializers.ModelSerializer):
    """
    Serializer for the RoomGroup model.
    """
    class Meta:
        model = RoomGroup
        fields = '__all__'

class RoomSerializer(serializers.ModelSerializer):
    """
    Serializer for the Room model.
    Includes nested representation of the associated RoomGroup.
    """
    group = RoomGroupSerializer(read_only=True)
    
    class Meta:
        model = Room
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomUser model.
    Provides a nested view of allowed_room_groups.
    """
    allowed_room_groups = RoomGroupSerializer(many=True, read_only=True)
    
    class Meta:
        model = CustomUser
        # Include key fields for authentication and profile display.
        fields = ['id', 'username', 'email', 'is_admin', 'is_approved', 'allowed_room_groups', 'face_reference_image', 'voice_reference']

class AccessLogSerializer(serializers.ModelSerializer):
    """
    Serializer for successful authentication logs.
    Provides a nested representation of the user and room.
    """
    user = UserSerializer(read_only=True)
    room = RoomSerializer(read_only=True)
    
    class Meta:
        model = AccessLog
        fields = '__all__'

class DeniedLogSerializer(serializers.ModelSerializer):
    """
    Serializer for denied authentication attempts.
    Provides a nested representation of the user and room.
    """
    user = UserSerializer(read_only=True)
    room = RoomSerializer(read_only=True)
    
    class Meta:
        model = DeniedLog
        fields = '__all__'
