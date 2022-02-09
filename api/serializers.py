from .models import Assignment, Submissions, User, UserClass
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken


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
    pk = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)
    fullname = serializers.CharField(read_only=True)
    token = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)
    _class = serializers.CharField(read_only=True, max_length=20)
    submissions = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    assignments = serializers.PriamryKeyRelatedField(many=True, read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def validate(self, data):
        email = data['email']
        password = data['password']
        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError("Email or password incorrect!")

        try:
            refresh = RefreshToken.for_user(user)
            # refresh_token = str(refresh)
            token = str(refresh.access_token)
            update_last_login(None, user)
            data.update(
                pk=user.pk,
                token=token,
                role=user.role,
                _class=user._class.name,
                fullname=user.fullname
            )
            # validated_data = {
            #     'token': token,
            #     'email': user.email,
            #     'role': user.role,
            #     '_class': user._class.name,
            #     'fullname': user.fullname,
            # }
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
    submissions = serializers.StringRelatedField(many=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=False)
    _class_id = serializers.PrimaryKeyRelatedField(
        queryset=UserClass.objects.all(), many=False)

    class Meta:
        model = Assignment
        fields = ('title', 'course', 'course_code', 'author_id',
                  '_class_id', 'duration', 'status', 'marks', 'submissions')

    def validate(self, data):
        author = data['author']
        user = User.objects.get(name=author)
        if user.role != 'INSTRUCTOR' or user is None:
            raise serializers.ValidationError(
                'Only Instructors can create assignments')


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

    def validate(self, data):
        author = data['author']
        user = User.objects.get(name=author)
        if user.role != 'STUDENT' or user is None:
            raise serializers.ValidationError(
                'Only Students can create submissions')
