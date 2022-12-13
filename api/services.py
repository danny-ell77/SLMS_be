import pathlib
from uuid import uuid4
from .models import CourseMaterial
from .aws_integrations import s3_generate_presigned_post
from django.utils import timezone
from django.shortcuts import get_object_or_404
from api.models import User


def file_generate_name(original_file_name):
    extension = pathlib.Path(original_file_name).suffix

    return f"{uuid4().hex}{extension}"


class CourseMaterialService:
    @classmethod
    def save(cls, request, file_name, file_type, classroom):
        user = get_object_or_404(User, pk=request.user.pk)
        cm = CourseMaterial(
            original_file_name=file_name,
            file_name=file_generate_name(file_name),
            file_type=file_type,
            uploaded_by=user,
            classroom=classroom,
            file=None,
        )
        cm.save()
        return cm


class FileDirectUploadService:
    @classmethod
    def start(cls, entity, file_name, file_type, **kwargs):
        upload_path = f"file/{file_name}"
        entity.file = entity.file.field.attr_class(
            entity, entity.file.field, upload_path
        )

        entity.save()

        presigned_data = s3_generate_presigned_post(
            file_path=upload_path, file_type=file_type
        )

        return {"id": entity.id, **presigned_data}

    @classmethod
    def finish(cls, file):
        file.upload_finished_at = timezone.now()
        file.full_clean()
        file.save()

        return file
