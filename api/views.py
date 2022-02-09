from django.http import Http404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import authentication, permissions

from .models import Assignment, Submissions, User
from .serializers import (AssignmentSerializer, SubmissionSerializer,
                          UserListSerializer, UserLoginSerializer,
                          UserRegistrationSerializer)


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

    def get(self, request):
        submissions = Submissions.objects.all()
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
    only Instructors can list all submissions
    Only Students can create submissions
    '''
    serializer_class = AssignmentSerializer
    authentication_classes = [authentication.TokenAuthentication]

    def get(self, request):
        assignments = Assignment.objects.all()
        serializer = self.serializer_class(assignments, many=True)
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
