from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError(
                "Credenciales inválidas, por favor verifica tu usuario y contraseña.")
        if not user.is_active:
            raise serializers.ValidationError("Esta cuenta está desactivada.")

        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email',
                  'first_name', 'last_name', 'password', 'is_active', 'is_staff', 'is_superuser')

        extra_kwargs = {
            'is_superuser': {'read_only': False},
            'is_staff': {'read_only': False}
        }

    def create(self, validated_data):
        """
        Sobrescribe el método create para manejar el hash de la contraseña.
        """
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Sobrescribe el método update para manejar el hash de la contraseña.
        """
        if 'password' in validated_data:
            validated_data['password'] = make_password(
                validated_data['password'])
        return super().update(instance, validated_data)
