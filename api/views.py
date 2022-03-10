from os import access
from tokenize import cookie_re
from turtle import st

from django.http import Http404
from rest_framework import authentication, permissions, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Assignment, Submissions, User, UserClass
from .serializers import (AssignmentSerializer, CookieTokenRefreshSerializer,
                          SubmissionSerializer, UserListSerializer,
                          UserLoginSerializer, UserRegistrationSerializer)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return dict(
        refresh=str(refresh),
        access=str(refresh.access)
    )


class CookieTokenObtainPairView(TokenObtainPairView):
    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get('token'):
            cookie_max_age = 3600 * 24 * 14  # 14 days
            response.set_cookie(
                'refresh_token', response.data['refresh_token'], max_age=cookie_max_age, httpOnly=True)
            del response.data['refresh_token']
        return super().finalize_response(request, response, *args, **kwargs)


class CookieTokenRefreshView(TokenRefreshView):
    serializer_class = CookieTokenRefreshSerializer

    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get('refresh'):
            cookie_max_age = 3600 * 24 * 14  # 14 days
            response.set_cookie(
                'refresh_token', response.data['refresh'], max_age=cookie_max_age, httponly=True)
            del response.data['refresh']
        return super().finalize_response(request, response, *args, **kwargs)


class UserLoginView(APIView):
    serializer_class = UserLoginSerializer
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        valid = serializer.is_valid(raise_exception=True)

        if valid:
            status_code = status.HTTP_200_OK

            response = {
                'success': True,
                'message': 'succesful login!',
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
            serializer.save()
            status_code = status.HTTP_201_CREATED

            response = {
                'success': True,
                'message': 'User successfully registered!',
                'user': serializer.data
            }

            return Response(response, status=status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(APIView):
    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        # print(dir(request.user))
        id = request.user.pk
        user = User.objects.get(pk=id)
        if user.role != 'ADMIN':
            response = {
                'success': False,
                'status_code': status.HTTP_403_FORBIDDEN,
                'message': 'You are not authorized to perform this action'
            }
            return Response(response, status.HTTP_403_FORBIDDEN)
        else:
            users = User.objects.all()
            serializer = self.serializer_class(users, many=True)
            response = {
                'success': True,
                'status_code': status.HTTP_200_OK,
                'message': 'Successfully fetched users',
                'users': serializer.data

            }
            return Response(response, status=status.HTTP_200_OK)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            return UserClass.objects.get(pk=id)
        except UserClass.DoesNotExist:
            raise Http404

    def get(self, request):
        user = request.user
        if user.role == "INSTRUCTOR":
            submissions = Submissions.objects.get(lecturer=user.id)
        else:
            class_instance = request.user._class
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
            _class_id = user._class.id
            assignments = Assignment.objects.get(_class=_class_id)
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
