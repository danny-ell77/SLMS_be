from pprint import pprint
from urllib import response

from django.conf import settings
from django.http import Http404
from rest_framework import authentication, permissions, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .models import Assignment, ClassRoom, Instructor, Student, Submission, User
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
print(cookie_details)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return dict(
        refresh=str(refresh),
        access=str(refresh.access_token)
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
        if valid:
            user = User.objects.get(pk=serializer.data['pk'])
            auth_tokens = get_tokens_for_user(user)
            response = Response()
            response.set_cookie(value=auth_tokens["refresh"], **cookie_details)
            print(response)
            response.data = {
                'success': True,
                'message': 'You have logged in successfully',
                'token': auth_tokens["access"],
                'user': serializer.data
            }
            response.status_code = status.HTTP_200_OK
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegistrationView(APIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        valid = serializer.is_valid(raise_exception=True)

        if valid:
            response = Response()
            user = serializer.save()
            auth_tokens = get_tokens_for_user(user)
            response.set_cookie(value=auth_tokens["refresh"], **cookie_details)
            response.data = {
                'success': True,
                'message': 'Registration complete, welcome to SIMS!',
                'token': auth_tokens["access"],
                'user': serializer.data
            }
            response.status_code = status.HTTP_201_CREATED

            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AssignmentsListView(APIView):
    '''
    List all Assignments or create a new one.
    Students & Instructors can list all assignments by Class
    and id respectively
    Only Instructors can create assignments
    '''
    serializer_class = AssignmentSerializer

    def get(self, request):
        auth_user = request.user
        # pprint(dir(user))
        user = User.objects.get(pk=auth_user.pk)
        if user.is_instructor:
            assignments = Assignment.objects.filter(instructor=user.instructor)
        else:
            classroom_id = user.student.classroom.id
            assignments = Assignment.objects.filter(classroom=classroom_id)
        serializer = self.serializer_class(assignments, many=True)
        response_data = {
            'success': True,
            'message': 'Assignments fetched successfully',
            'data': serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response_data = {
                'success': True,
                'message': 'Assignment created successfully',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
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
        response_data = {
            'success': True,
            'message': 'Assignment fetched successfully',
            'data': serializer.data
        }
        return Response(response_data)

    def patch(self, request, id):
        user = User.objects.get(pk=request.user.pk)
        if user.is_instructor:
            assignment = self.get_object(id)
            serializer = self.serializer_class(assignment, data=request.data)
            if serializer.is_valid():
                serializer.save()
                response_data = {
                    'success': True,
                    'message': 'Assignment updated successfully',
                    'data': serializer.data
                }
                return Response(response_data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Only Instructors can Update Assignments'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        print(id)
        assignment = self.get_object(id)
        assignment.delete()
        response_data = {
            'success': True,
            'message': 'Assignment deleted successfully',
        }
        return Response(response_data, status=status.HTTP_204_NO_CONTENT)


class SubmissionListView(APIView):
    '''
    List all Submission or create a new one.
    Students & Instructors can list all assignments by id
    and class respectively
    Only Students can create assignments
    '''
    serializer_class = SubmissionSerializer

    def get(self, request):
        auth_user = request.user
        user = User.objects.get(pk=auth_user.pk)
        if user.is_instructor:
            submissions = Submission.objects.filter(instructor=user.instructor)
        else:
            submissions = Submission.objects.filter(student=user.student)
        serializer = self.serializer_class(submissions, many=True)
        response_data = {
            'success': True,
            'message': 'Submissions fetched successfully',
            'data': serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response_data = {
                'success': True,
                'message': 'Submission created successfully',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubmissionsDetailView(APIView):
    """
    Retrieve, update or delete a post instance.
    """

    serializer_class = SubmissionSerializer

    def get_object(self, id):
        try:
            return Submission.objects.get(pk=id)
        except Submission.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):
        submission = self.get_object(id)
        serializer = self.serializer_class(submission)
        return Response(serializer.data)

    def patch(self, request, id, format=None):
        '''
        Students are only capable of 
        '''
        auth_user = request.user
        user = User.objects.get(pk=auth_user.pk)
        submission = self.get_object(id)
        serializer = self.serializer_class(submission, data=request.data)
        if serializer.is_valid(raise_exception=True):
            if user.is_instructor:
                serializer.save()
                response_data = {
                    'success': True,
                    'message': 'Submission marked successfully',
                    'data': serializer.data
                }
                return Response(response_data, status=status.HTTP_200_OK)
            response_data = {
                'success': False,
                'message': 'Only Instructors can mark assignments',
                'data': serializer.errors
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        print(id)
        submission = self.get_object(id)
        submission.delete()
        response_data = {
            'success': True,
            'message': 'Submission deleted successfully',
        }
        return Response(response_data, status=status.HTTP_204_NO_CONTENT)
