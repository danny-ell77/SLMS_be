from dataclasses import field
from os import access
from pickletools import read_long1
from jwt import InvalidTokenError
from .models import Assignment, ClassRoom, CourseMaterial, Instructor, Student, Submission, User
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class CookieTokenRefreshSerializer(TokenRefreshSerializer):
    refresh = None

    def validate(self, attrs):
        attrs['refresh'] = self.context['request'].COOKIES.get('refresh_token')
        refresh = RefreshToken(attrs['refresh'])
        attrs['lifetime'] = int(
            refresh.access_token.lifetime.total_seconds())
        attrs['access'] = str(refresh.access_token)

        if attrs['refresh']:
            return attrs
        else:
            raise InvalidTokenError(
                'No valid token found in cookie  \'refresh_token\'')


class SubmissionSerializer(serializers.ModelSerializer):
    assignment = serializers.PrimaryKeyRelatedField(
        queryset=Assignment.objects.all(), many=False)
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),  many=False)
    instructor = serializers.PrimaryKeyRelatedField(
        queryset=Instructor.objects.all(), many=False)
    classroom = serializers.PrimaryKeyRelatedField(
        queryset=ClassRoom.objects.all(), many=False)

    class Meta:
        model = Submission
        fields = ('id', 'assignment', 'student', 'instructor', 'classroom', 'content',
                  'title', 'status', 'score', 'is_draft', 'is_submitted')

    def create(self, validated_data):
        submission = Submission.objects.filter(
            content=validated_data.get('content')).first()
        if submission:
            raise serializers.ValidationError(
                'This submission already exists!, consider changing the Title or content')
        return super().create(validated_data)


class AssignmentSerializer(serializers.ModelSerializer):
    instructor = serializers.PrimaryKeyRelatedField(
        queryset=Instructor.objects.all(), many=False)
    classroom = serializers.PrimaryKeyRelatedField(
        queryset=ClassRoom.objects.all(), many=False)

    class Meta:
        model = Assignment
        fields = ('id', 'title', 'course', 'course_code', 'instructor',
                  'classroom', 'status', 'marks')

    def create(self, validated_data):
        assignment = Assignment.objects.filter(
            title=validated_data.get('title')).first()
        if assignment:
            raise serializers.ValidationError(
                'This assignment already exists!')
        return super().create(validated_data)


class ClassRoomSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    assignments = serializers.StringRelatedField(many=True)

    class Meta:
        model = ClassRoom
        fields = ('name', 'assignments', )


class StudentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    classroom = ClassRoomSerializer()
    # submissions = serializers.StringRelatedField(many=True)
    submissions = serializers.StringRelatedField(read_only=True, many=True)

    class Meta:
        model = Student
        fields = ('id', 'classroom', 'submissions', )


class InstructorSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    assignments = serializers.StringRelatedField(many=True)

    class Meta:
        model = Instructor
        fields = ('id', 'assignments', )


class UserRegistrationSerializer(serializers.Serializer):
    student = StudentSerializer(read_only=True)
    instructor = InstructorSerializer(read_only=True)
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
        user = User.objects.get(email=validated_data['email'])
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
    student = StudentSerializer(read_only=True)
    instructor = InstructorSerializer(read_only=True)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)
    fullname = serializers.CharField(read_only=True)
    is_student = serializers.BooleanField(read_only=True)
    is_instructor = serializers.BooleanField(read_only=True)

    def validate(self, attrs):
        email = attrs['email']
        password = attrs['password']
        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError(
                "Email or password is incorrect!")

        try:
            student = Student.objects.get(
                user=user) if user.is_student else None
            instructor = Instructor.objects.get(
                user=user) if user.is_instructor else None

            update_last_login(None, user)
            attrs.update(
                pk=user.pk,
                is_student=user.is_student,
                is_instructor=user.is_instructor,
                fullname=user.fullname,
                student=student,
                instructor=instructor
            )
            return attrs
        except:
            raise serializers.ValidationError("Email or password incorrect")


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'role'
        )


class CourseMaterialSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField(many=False, read_only=True)

    def create(self, validated_data):
        auth_user = self.context["request"].user
        user = User.objects.get(pk=auth_user.pk)
        # print(dir(self.context))
        cm = CourseMaterial.objects.create(uploaded_by=user, **validated_data)
        return cm

    class Meta:
        model = CourseMaterial
        fields = "__all__"
