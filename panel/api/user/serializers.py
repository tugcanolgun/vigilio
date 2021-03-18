from dataclasses import dataclass

from rest_framework import serializers


@dataclass
class ChangePasswordData:
    current_password: str
    new_password: str


class ChangePasswordSerializer(serializers.Serializer):
    currentPassword = serializers.CharField(max_length=255, required=True)
    newPassword = serializers.CharField(max_length=255, required=True)

    @property
    def object(self) -> ChangePasswordData:
        return ChangePasswordData(
            current_password=self.validated_data["currentPassword"],
            new_password=self.validated_data["newPassword"],
        )
