"""
Serializers for the user API View.
"""
from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _


from rest_framework import serializers

from core.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = ["email", "password", "name"]
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        return self.Meta.model.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user: User = super().update(instance=instance, validated_data=validated_data)

        if password:
            user.set_password(raw_password=password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""

    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"},
        trim_whitespace=False,
    )

    def validate(self, attrs: dict):
        email = attrs.get("email")
        password = attrs.get("password")

        user: User = authenticate(
            request=self.context.get("request"), username=email, password=password
        )

        if not user:
            msg = _("Unable to authenticate with provided credentials.")
            # * this is the standar way to raise errors with serializers
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs
