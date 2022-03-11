from django.conf import settings
from django.http import Http404
from rest_framework import authentication, permissions, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Assignment, Submissions, User, ClassRoom
from .serializers import (AssignmentSerializer, CookieTokenRefreshSerializer,
                          SubmissionSerializer, UserListSerializer,
                          UserLoginSerializer, UserRegistrationSerializer)

cookie_details = dict(
    key=settings.SIMPLE_JWT['AUTH_COOKIE'],
    expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
    secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
    httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
    samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return dict(
        refresh=str(refresh),
        access=str(refresh.access)
    )


class CookieTokenRefreshView(TokenRefreshView):
    serializer_class = CookieTokenRefreshSerializer

    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get('refresh'):
            response.set_cookie(
                value=response.data["refresh"], **cookie_details)
            del response.data['refresh']
        return super().finalize_response(request, response, *args, **kwargs)


class UserLoginView(APIView):
    serializer_class = UserLoginSerializer
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        valid = serializer.is_valid(raise_exception=True)
        response = Response()
        if valid:
            status_code = status.HTTP_200_OK
            user = User.objects.get(pk=serializer.data.id)
            auth_tokens = get_tokens_for_user(user)
            response.set_cookie(value=auth_tokens["refresh"], **cookie_details)
            response = {
                'success': True,
                'message': 'You have logged in successfully',
                'token': auth_tokens["access"],
                'user': serializer.data
            }

            return Response(response, status=status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegistrationView(APIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        valid = serializer.is_valid(raise_exception=True)

        if valid:
            user = serializer.save()
            status_code = status.HTTP_201_CREATED
            auth_tokens = get_tokens_for_user(user)
            response.set_cookie(value=auth_tokens["refresh"], **cookie_details)
            response = {
                'success': True,
                'message': 'Registration complete, welcome to SIMS!',
                'token': auth_tokens["access"],
                'user': serializer.data
            }

            return Response(response, status=status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubmissionListView(APIView):
    '''
    List all Submissions or create a new one,
    only Instructors can list all submissions
    Only Students can create submissions
    '''
    serializer_class = SubmissionSerializer
    authentication_classes = [authentication.TokenAuthentication]

    def get_user_class(self, id):
        try:
            return ClassRoom.objects.get(pk=id)
        except ClassRoom.DoesNotExist:
            raise Http404

    def get(self, request):
        user = request.user
        if user.role == "INSTRUCTOR":
            submissions = Submissions.objects.get(lecturer=user.id)
        else:
            class_instance = request.user.classroom
            user_class = self.get_user_class(class_instance.id)
            submissions = user_class.submissions.all()
        serializer = self.serializer_class(submissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubmissionsDetailView(APIView):
    """
    Retrieve, update or delete a post instance.
    """

    serializer_class = SubmissionSerializer

    def get_object(self, id):
        try:
            return Submissions.objects.get(pk=id)
        except Submissions.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):
        submission = self.get_object(id)
        serializer = self.serializer_class(submission)
        return Response(serializer.data)

    def put(self, request, id, format=None):
        '''
        Students are only capable of 
        '''
        submission = self.get_object(id)
        serializer = self.serializer_class(submission, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug, format=None):
        submission = self.get_object(id)
        submission.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssignmentsListView(APIView):
    '''
    List all Assignments or create a new one,
    only Instructors can list all assignments
    Only Students can create assignments
    '''
    serializer_class = AssignmentSerializer
    # authentication_classes = [authentication.TokenAuthentication]

    def get(self, request):
        user = request.user
        if user.role == "INSTRUCTOR":
            assignments = Assignment.objects.get(author_id=user.pk)
        else:
            classrom_id = user.classroom.id
            assignments = Assignment.objects.get(classroom=classrom_id)
        serializer = self.serializer_class(assignments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AssignmentsDetailView(APIView):
    """
    Retrieve, update or delete assignment instance.
    """

    serializer_class = AssignmentSerializer

    def get_object(self, id):
        try:
            return Assignment.objects.get(pk=id)
        except Assignment.DoesNotExist:
            raise Http404

    def get(self, request, id):
        assignment = self.get_object(id)
        serializer = self.serializer_class(assignment)
        return Response(serializer.data)

    def put(self, request, id):
        assignment = self.get_object(id)
        serializer = self.serializer_class(assignment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        assignment = self.get_object(id)
        assignment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
