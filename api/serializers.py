from jwt import InvalidTokenError
from .models import Assignment, ClassRoom, Instructor, Student, Submissions, User
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
    classroom = serializers.CharField(max_length=10)

    class Meta:
        model = User
        fields = (
            'firstname',
            'lastname',
            'email',
            'is_student',
            'is_instructor',
            'password',
            'classroom'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        print(f"validated_data ==> {validated_data}")
        classroom = validated_data.pop('classroom')
        user = User.objects.create(**validated_data)
        if validated_data.get('is_student') != None:
            user_class = ClassRoom.objects.get(name=classroom)
            Student.objects.create(user=user, classroom=user_class)
        if validated_data.get('is_instructor') != None:
            Instructor.objects.create(user)
        return user


class UserLoginSerializer(serializers.Serializer):
    pk = serializers.CharField(read_only=True, max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)
    fullname = serializers.CharField(read_only=True)
    classroom = serializers.CharField(read_only=True, max_length=20)
    # submissions = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    # assignments = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    def validate(self, attrs):
        email = attrs['email']
        password = attrs['password']
        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError(
                "Email or password is incorrect!")

        if user.is_student:
            student = Student.objects.get(user=user)
        else:
            student = None

        try:
            update_last_login(None, user)
            attrs.update(
                id=user.pk,
                is_student=user.is_student,
                is_instructor=user.is_instructor,
                fullname=user.fullname,
                student=student
            )
            return attrs
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
    classrom_id = serializers.PrimaryKeyRelatedField(
        queryset=ClassRoom.objects.all(), many=False)

    class Meta:
        model = Assignment
        fields = ('title', 'course', 'course_code', 'author_id',
                  'classrom_id', 'status', 'marks', 'submissions')

    def create(self, data):
        author = data['author_id']
        classroom = data['classrom_id']
        print(data)
        # user = User.objects.get(pk=author)
        if author.role == 'STUDENT' or author is None:
            raise serializers.ValidationError(
                'Only Instructors can create assignments')
        data.update(author_id=author.id, classrom_id=classroom.id)
        return data


class SubmissionSerializer(serializers.ModelSerializer):
    assignment = serializers.PrimaryKeyRelatedField(
        queryset=Assignment.objects.all(), many=False)
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),  many=False)
    classroom = serializers.PrimaryKeyRelatedField(
        queryset=ClassRoom.objects.all(), many=False)

    class Meta:
        model = Submissions
        fields = ('assignment', 'author', 'classroom', 'content',
                  'title', 'status', 'score', 'is_draft', 'is_submitted')

    def create(self, data):
        author = data['author']
        user = User.objects.get(name=author)
        if user.role == 'INSTRUCTOR' or user is None:
            raise serializers.ValidationError(
                'Only Students can create submissions')
