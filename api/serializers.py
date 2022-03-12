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


class StudentSerializer(serializers.ModelSerializer):
    classroom = serializers.StringRelatedField(many=False)

    class Meta:
        model = Student
        fields = ('classroom',)


class UserRegistrationSerializer(serializers.Serializer):
    student = StudentSerializer(read_only=True)
    classroom = serializers.CharField(write_only=True, allow_blank=True)
    pk = serializers.CharField(read_only=True, max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)
    firstname = serializers.CharField()
    lastname = serializers.CharField()
    is_student = serializers.BooleanField()
    is_instructor = serializers.BooleanField(required=False)

    def create(self, validated_data):
        print(f"validated_data ==> {validated_data}")
        classroom = validated_data.pop('classroom')
        print(validated_data)
        user = User.objects.filter(email=validated_data['email']).first()
        if not user:
            user = User.objects.create_user(**validated_data)
            if validated_data.get('is_student') == True:
                user_class = ClassRoom.objects.get(name=classroom)
                Student.objects.create(user=user, classroom=user_class)
            elif validated_data.get('is_instructor') == True:
                Instructor.objects.create(user=user)
            return user
        else:
            raise serializers.ValidationError(
                "A user with this email already exists")


class UserLoginSerializer(serializers.Serializer):
    pk = serializers.CharField(read_only=True, max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)
    fullname = serializers.CharField(read_only=True)
    classroom = serializers.CharField(read_only=True, max_length=20)
    is_student = serializers.BooleanField(read_only=True)
    is_instructor = serializers.BooleanField(read_only=True)
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
            print(attrs)
            attrs.update(
                pk=user.pk,
                is_student=user.is_student,
                is_instructor=user.is_instructor,
                fullname=user.fullname,
                classroom=student.classroom
            )
            print(attrs)
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
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=False)
    classroom = serializers.PrimaryKeyRelatedField(
        queryset=ClassRoom.objects.all(), many=False)

    class Meta:
        model = Assignment
        fields = ('id', 'title', 'course', 'course_code', 'author',
                  'classroom', 'status', 'marks', 'submissions')

    def create(self, validated_data):
        assignment = Assignment.objects.filter(
            title=validated_data.get('title')).first()
        if assignment:
            raise serializers.ValidationError(
                'This assignment already exists!')
        return super().create(validated_data)

    # def validate(self, data):
    #     author = data['author']
    #     print(data, author.is_student)
    #     if author.is_student:
    #         raise serializers.ValidationError(
    #             'Only Instructors can create or update Assignments')
    #     return data


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
