from rest_framework import serializers

from accounts.models import User, Profile
from accounts.serializers.roles_permissions import SimpleRoleSerializer
from accounts.models import Role


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'bio',
            'website',
        ]
        read_only_fields = fields


class RoleIdsField(serializers.PrimaryKeyRelatedField):
    def __init__(self, **kwargs):
        super().__init__(many=True, queryset=Role.objects.all(), **kwargs)

    def to_representation(self, value):
        # Represent as list of role IDs
        return value.values_list('id', flat=True) if hasattr(value, 'values_list') else value.id


class CreateUserSerializer(serializers.ModelSerializer):
    role_ids = RoleIdsField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'username',
            'full_name',
            'phone_number',
            'email',
            'role_ids',
        ]

    def create(self, validated_data):
        roles = validated_data.pop('role_ids', [])
        user = super().create(validated_data)
        if roles:
            user.roles.set(roles)
        return user


class EditUserSerializer(serializers.ModelSerializer):
    role_ids = RoleIdsField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'full_name',
            'phone_number',
            'email',
            'role_ids',
        ]

    def update(self, instance, validated_data):
        roles = validated_data.pop('role_ids', None)
        instance = super().update(instance, validated_data)
        if roles is not None:
            instance.roles.set(roles)
        return instance


class GetUserSerializer(serializers.ModelSerializer):
    roles = SimpleRoleSerializer(many=True, read_only=True)
    profile = ProfileSerializer(read_only=True)
    role_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text='List of role IDs to assign'
    )

    class Meta:
        model = User
        fields = [
            'username',
            'full_name',
            'phone_number',
            'email',
            'user_type',
            'status',
            'is_verified',
            'update_kyc_required',
            'headline_title',
            'about',
            'followers_count',
            'following_count',
            'deals_joined',
            'roles',
            'role_ids',
            'profile',
            'created_at',
            'updated_at',
        ]

    def update(self, instance, validated_data):
        # Reuse EditUser logic
        roles = validated_data.pop('role_ids', None)
        instance = super().update(instance, validated_data)
        if roles is not None:
            instance.roles.set(roles)
        return instance


class UserListSerializer(serializers.ModelSerializer):
    roles = SimpleRoleSerializer(many=True, read_only=True)
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'username',
            'full_name',
            'phone_number',
            'email',
            'user_type',
            'status',
            'roles',
            'profile',
            'created_at',
            'updated_at',
        ]


class ActivateOrDeactivateUserSerializer(serializers.Serializer):
    is_active = serializers.BooleanField()
    reason = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class CheckUsernameSerializer(serializers.Serializer):
    username = serializers.CharField()
    count = serializers.IntegerField(required=False, min_value=1)
