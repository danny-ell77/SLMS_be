from jwt import InvalidTokenError
from .models import Assignment, ClassRoom, CourseMaterial, Instructor, Student, Submission, User
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q


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


class AssignmentSerializer(serializers.ModelSerializer):
    instructor_name = serializers.StringRelatedField(
        source="instructor", read_only=True, many=False)
    classroom = serializers.SlugRelatedField(
        slug_field='name',
        queryset=ClassRoom.objects.all(), many=False)

    class Meta:
        model = Assignment
        fields = ('id', 'question', 'course', 'code',
                  'classroom', 'status', 'marks', 'due', 'instructor', 'instructor_name')
        extra_kwargs = {'instructor': {'read_only': True}}

    def create(self, validated_data):
        assignment = Assignment.objects.filter(
            question=validated_data.get('question')).first()
        if assignment:
            raise serializers.ValidationError(
                'This assignment already exists!')
        auth_user = self.context["request"].user
        validated_data["instructor"] = auth_user.instructor
        return super().create(validated_data)


class SubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.StringRelatedField(
        source="student", read_only=True, many=False)
    instructor_name = serializers.StringRelatedField(
        source="instructor", read_only=True, many=False)
    classroom = serializers.SlugRelatedField(
        slug_field='name',
        queryset=ClassRoom.objects.all(), many=False)
    # assignment = serializers.SlugRelatedField(
    #     slug_field='code',
    #     queryset=Assignment.objects.all(), many=False)

    class Meta:
        model = Submission
        fields = ('id', 'student_name', 'instructor_name', 'assignment', 'instructor', 'classroom', 'content',
                  'title', 'status', 'score', 'is_draft', 'is_submitted')
        extra_kwargs = {
            'instructor': {'write_only': True},
            'is_submitted': {'read_only': True},
        }

    def create(self, validated_data):
        submission = Submission.objects.filter(
            content=validated_data.get('content')).first()
        # s = Submission.objects.get(
        #     Q(content__icontains=validated_data.get('content') | Q(title__contains=validated_data.get('title'))))
        if submission and submission.status == "SUBMITTED":
            raise serializers.ValidationError(
                'This submission already exists!, consider changing the Title or content')
        auth_user = self.context["request"].user
        validated_data["student"] = auth_user.student
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
        user = User.objects.filter(email=validated_data['email']).exists()
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
        # print(dir(self.context))
        cm = CourseMaterial.objects.create(
            uploaded_by=auth_user, **validated_data)
        return cm

    class Meta:
        model = CourseMaterial
        fields = "__all__"
