import pathlib
from uuid import uuid4
from .models import CourseMaterial
from .aws_integrations import s3_generate_presigned_post
from django.utils import timezone

# def create_assignment_service(reequest, validated_data):
#     assignment = Assignment.objects.filter(
#         question=validated_data.get('question')).first()
#     if assignment:
#         raise ValidationError(
#             'This assignment already exists!')
#     auth_user = request.user
#     validated_data["instructor"] = auth_user.instructor
#     return Assignments.objects.create(validated_data)


def file_generate_name(original_file_name):
    extension = pathlib.Path(original_file_name).suffix

    return f"{uuid4().hex}{extension}"


class FileDirectUploadService:
    def __init__(self, user) -> None:
        self.user = user

    def start(self, file_name, file_type, classroom):
        cm = CourseMaterial(
            original_file_name=file_name,
            file_name=file_generate_name(file_name),
            file_type=file_type,
            uploaded_by=self.user,
            classroom=classroom,
            file=None,
        )
        cm.save()
        upload_path = f"file/{cm.file_name}"
        cm.file = cm.file.field.attr_class(cm, cm.file.field, upload_path)

        cm.save()

        presigned_data = s3_generate_presigned_post(
            file_path=upload_path, file_type=cm.file_type
        )

        return {"id": cm.id, **presigned_data}

    def finish(self, file):
        file.upload_finished_at = timezone.now()
        file.full_clean()
        file.save()

        return file
