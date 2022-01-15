from .models import User
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'password',
            '_class',
            'role',
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        auth_user = User.objects.create_user(**validated_data)
        return auth_user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)
    fullname = serializers.CharField(read_only=True)
    token = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)
    _class = serializers.CharField(read_only=True, max_length=20)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def validate(self, data):
        email = data['email']
        password = data['password']
        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid login credentials")

        try:

            refresh = RefreshToken.for_user(user)
            # refresh_token = str(refresh)
            token = str(refresh.access_token)
            update_last_login(None, user)

            validated_data = {
                'token': token,
                'email': user.email,
                'role': user.role,
                '_class': user._class,
                'fullname': user.fullname

            }
            return validated_data
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid login credentials")


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'role'
        )
