from django.db.models import Sum, Q
from django.http import Http404
from rest_framework import parsers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import time
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView
from api.permissions import IsInstructorOrReadOnly, IsStudentOrReadOnly
from .services import FileDirectUploadService, CourseMaterialService
from .models import (
    Assignment,
    CourseMaterial,
    Submission,
    User,
)
from django.apps import apps

from .serializers import (
    AssignmentSerializer,
    CookieTokenRefreshSerializer,
    CourseMaterialSerializer,
    SubmissionSerializer,
    UserLoginSerializer,
    UserRegistrationSerializer,
    CourseMaterialUploadSerializer,
    CourseMaterialFinishSerializer,
    AttachmentFinishSerializer,
    UserSerializer,
)
from .utils import cookie_details, get_tokens_for_user


class CookieTokenRefreshView(TokenRefreshView):
    serializer_class = CookieTokenRefreshSerializer

    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get("refresh"):
            response.set_cookie(value=response.data["refresh"], **cookie_details)
            del response.data["refresh"]
        return super().finalize_response(request, response, *args, **kwargs)


class AccountInformation(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = User.objects.get(pk=request.user.pk)
        if user.is_instructor:
            data = {}
        else:
            profile = user.student
            data = {
                "cumulative_grades": self._get_cumulative_grades(profile),
                "total_assignments": self._get_total_assignments(profile),
                "submissions_progress": self._get_submissions_progress(profile),
                "latest_course_materials": self._get_latest_entities(
                    profile, "CourseMaterial", CourseMaterialSerializer
                ),
                "latest_assignments": self._get_latest_entities(
                    profile, "Assignment", AssignmentSerializer
                ),
            }

        return Response(status=status.HTTP_200_OK, data=data)

    def patch(self, request):
        user = get_object_or_404(User, pk=request.user.pk)
        print(request.data)
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        print(user.fullname)
        data = {
            "success": True,
            "message": "Profile updated successfully",
            "data": serializer.data,
        }
        return Response(data=data, status=status.HTTP_200_OK)

    def _get_cumulative_grades(self, profile):

        score = profile.submissions.all().aggregate(total_score=Sum("score"))
        marks = profile.classroom.assignments.aggregate(total_marks=Sum("marks"))

        return f"{score['total_score'] / marks['total_marks']:.2f}"

    def _get_total_assignments(self, profile):
        return profile.classroom.assignments.all().count()

    def _get_submissions_progress(self, profile):
        aqs = profile.classroom.assignments.all().count()
        sqs = profile.submissions.filter(
            Q(status="SUBMITTED") & Q(student=profile)
        ).count()
        print(aqs, sqs)
        # sqs = Submission.objects.filter(student=user.student).count()
        # aqs = Submission.objects.filter(
        #     Q(status="SUBMITTED") & Q(student=user.student)
        # ).count()
        if aqs == 0 and sqs == 0:
            return 0
        return f"{sqs / aqs * 100:.2f}"

    def _get_latest_entities(self, profile, klass, serializer_class):
        Model = apps.get_model("api", klass)
        qs = Model.objects.filter(classroom=profile.classroom)[:7]
        return serializer_class(qs, many=True).data


class UserLoginView(APIView):
    serializer_class = UserLoginSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        valid = serializer.is_valid(raise_exception=True)
        if valid:
            user = User.objects.get(pk=serializer.data["pk"])
            auth_tokens = get_tokens_for_user(user)
            response = Response()
            response.set_cookie(value=auth_tokens["refresh"], **cookie_details)
            print(response)
            response.data = {
                "success": True,
                "message": "You have logged in successfully",
                "token": auth_tokens["access"],
                "user": serializer.data,
            }
            response.status_code = status.HTTP_200_OK
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegistrationView(APIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        valid = serializer.is_valid(raise_exception=True)

        if valid:
            response = Response()
            user = serializer.save()
            auth_tokens = get_tokens_for_user(user)
            response.set_cookie(value=auth_tokens["refresh"], **cookie_details)
            response.data = {
                "success": True,
                "message": "Registration complete, welcome to SIMS!",
                "token": auth_tokens["access"],
                "user": serializer.data,
            }
            response.status_code = status.HTTP_201_CREATED

            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AssignmentsListView(APIView):
    """
    List all Assignments or create a new one.
    Students & Instructors can list all assignments by Class
    and id respectively
    Only Instructors can create assignments
    """

    serializer_class = AssignmentSerializer
    permission_classes = (IsInstructorOrReadOnly,)

    def get(self, request):
        assignments = Assignment.objects.get_assignments(user=request.user)
        serializer = self.serializer_class(assignments, many=True)
        response_data = {
            "success": True,
            "message": "Assignments fetched successfully",
            "data": serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "success": True,
                "message": "Assignment created successfully",
                "data": serializer.data,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AssignmentsDetailView(APIView):
    """
    Retrieve, update or delete assignment instance.
    """

    serializer_class = AssignmentSerializer
    permission_classes = (IsInstructorOrReadOnly,)

    def get_object(self, pk):
        try:
            return Assignment.objects.get(pk=pk)
        except Assignment.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        assignment = self.get_object(pk)
        serializer = self.serializer_class(assignment)
        response_data = {
            "success": True,
            "message": "Assignment fetched successfully",
            "data": serializer.data,
        }
        return Response(response_data)

    def patch(self, request, pk):
        if request.user.is_instructor:
            assignment = self.get_object(pk)
            serializer = self.serializer_class(assignment, data=request.data)
            if serializer.is_valid():
                serializer.save()
                response_data = {
                    "success": True,
                    "message": "Assignment updated successfully",
                    "data": serializer.data,
                }
                return Response(response_data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"error": "Only Instructors can Update Assignments"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        print(pk)
        assignment = self.get_object(pk)
        assignment.delete()
        response_data = {
            "success": True,
            "message": "Assignment deleted successfully",
        }
        return Response(response_data, status=status.HTTP_204_NO_CONTENT)


class SubmissionListView(APIView):
    """
    List all Submission or create a new one.
    Students & Instructors can list all assignments by id
    and class respectively
    Only Students can create assignments
    """

    serializer_class = SubmissionSerializer
    permission_classes = (IsStudentOrReadOnly,)

    def get(self, request):
        submissions = Submission.objects.get_submissions(user=request.user)
        serializer = self.serializer_class(submissions, many=True)
        response_data = {
            "success": True,
            "message": "Submissions fetched successfully",
            "data": serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request):
        presigned_data = None
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        submission = serializer.save()
        if serializer.validated_data.get("has_attachment", False):
            presigned_data = FileDirectUploadService.start(
                submission, **serializer.validated_data
            )
        response_data = {
            "success": True,
            "message": "Submission created successfully",
            "data": serializer.data,
            "attachment": presigned_data,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class SubmissionsDetailView(APIView):
    """
    Retrieve, update or delete a post instance.
    """

    serializer_class = SubmissionSerializer
    # permission_classes = (IsStudentOrReadOnly, )

    def get_object(self, pk):
        try:
            return Submission.objects.get(pk=pk)
        except Submission.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        submission = self.get_object(pk)
        serializer = self.serializer_class(submission)
        return Response(serializer.data)

    def patch(self, request, pk, format=None):  # Mark Submission
        """
        Only Instructors are capable of editing submissions after submission
        """
        submission = self.get_object(pk)
        print(submission.assignment.due.timestamp() * 1000, time.time(), "here====")
        serializer = self.serializer_class(submission, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if submission.assignment.due.timestamp() * 1000 < time.time():
            response_data = {
                "success": False,
                "message": "Cannot mark submission after submission date",
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        if request.user.is_student:
            serializer.save()
            response_data = {
                "success": True,
                "message": "Submission marked successfully",
                "data": serializer.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        response_data = {
            "success": False,
            "message": "Only Instructors can mark assignments",
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        print(pk)
        submission = self.get_object(pk)
        submission.delete()
        response_data = {
            "success": True,
            "message": "Submission deleted successfully",
        }
        return Response(response_data, status=status.HTTP_204_NO_CONTENT)


class CourseMaterialsListView(APIView):
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    serializer_class = CourseMaterialSerializer

    def get(self, request):
        course_materials = CourseMaterial.objects.get_course_materials(
            user=request.user
        )
        serializer = self.serializer_class(course_materials, many=True)
        response_data = {
            "success": True,
            "message": "Course Materials fetched successfully",
            "data": serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)


class CourseMaterialStartUpload(APIView):
    serializer_class = CourseMaterialUploadSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        cm = CourseMaterialService.save(request, **serializer.validated_data)
        presigned_data = FileDirectUploadService.start(cm, **request.data)

        return Response(data=presigned_data)


class CourseMaterialFinishUpload(APIView):
    serializer_class = CourseMaterialFinishSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        print(request.data)
        serializer.is_valid(raise_exception=True)

        file_id = serializer.validated_data["file_id"]

        file = get_object_or_404(CourseMaterial, id=file_id)
        FileDirectUploadService.finish(file=file)

        return Response({"id": file.id})


class AttachmentFinishUpload(APIView):
    serializer_class = AttachmentFinishSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        file_id = serializer.validated_data["file_id"]

        submission = get_object_or_404(Submission, id=file_id)
        FileDirectUploadService.finish(file=submission)

        return Response({"id": submission.id})
