from jwt import InvalidTokenError
from .models import Assignment, Submissions, User, UserClass
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.serializers import TokenRefreshSerializer


class CookieTokenRefreshSerializer(TokenRefreshSerializer):
    refresh = None

    def validate(self, attrs):
        attrs['refresh'] = self.context['request'].COOKIES.get('refresh_token')
        if attrs['refresh']:
            return super().validate(attrs)
        else:
            raise InvalidTokenError(
                'No valid token found in cookie  \'refresh_token\'')


class UserRegistrationSerializer(serializers.ModelSerializer):
    _class = serializers.CharField(max_length=10)

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
        print(f"validated_data ==> {validated_data}")
        class_instance = UserClass.objects.get(name=validated_data['_class'])
        validated_data['_class'] = class_instance
        auth_user = User.objects.create_user(**validated_data)
        return auth_user


class UserLoginSerializer(serializers.Serializer):
    pk = serializers.CharField(read_only=True, max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)
    fullname = serializers.CharField(read_only=True)
    token = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)
    _class = serializers.CharField(read_only=True, max_length=20)
    # submissions = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    # assignments = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    def validate(self, data):
        email = data['email']
        password = data['password']
        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError("Email or password incorrect!")

        try:
            # refresh_token = str(refresh)
            update_last_login(None, user)
            data.update(
                id=user.pk,
                role=user.role,
                _class=user._class.name,
                fullname=user.fullname
            )
            return data
        except User.DoesNotExist:
            raise serializers.ValidationError("Email or password incorrect")


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'role'
        )


class AssignmentSerializer(serializers.ModelSerializer):
    submissions = serializers.StringRelatedField(many=True, read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=False)
    _class_id = serializers.PrimaryKeyRelatedField(
        queryset=UserClass.objects.all(), many=False)

    class Meta:
        model = Assignment
        fields = ('title', 'course', 'course_code', 'author_id',
                  '_class_id', 'status', 'marks', 'submissions')

    def create(self, data):
        author = data['author_id']
        _class = data['_class_id']
        print(data)
        # user = User.objects.get(pk=author)
        if author.role == 'STUDENT' or author is None:
            raise serializers.ValidationError(
                'Only Instructors can create assignments')
        data.update(author_id=author.id, _class_id=_class.id)
        return data


class SubmissionSerializer(serializers.ModelSerializer):
    assignment = serializers.PrimaryKeyRelatedField(
        queryset=Assignment.objects.all(), many=False)
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),  many=False)
    _class = serializers.PrimaryKeyRelatedField(
        queryset=UserClass.objects.all(), many=False)

    class Meta:
        model = Submissions
        fields = ('assignment', 'author', '_class', 'content',
                  'title', 'status', 'score', 'is_draft', 'is_submitted')

    def create(self, data):
        author = data['author']
        user = User.objects.get(name=author)
        if user.role == 'INSTRUCTOR' or user is None:
            raise serializers.ValidationError(
                'Only Students can create submissions')
