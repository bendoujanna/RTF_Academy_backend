from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['uid', 'email', 'full_name', 'role', 'last_login', 'created_at']
        read_only_fields = ['uid', 'role', 'last_login', 'created_at']