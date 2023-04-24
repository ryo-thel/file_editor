from django.urls import path
from .views import (
    SambaFileListAPIView,
    SambaFileContentAPIView,
    SambaFileStreamAPIView,
    SambaFileUploadAPIView,
)

urlpatterns = [
    path("file_list/", SambaFileListAPIView.as_view(), name="samba_file_list"),
    path("file_content/", SambaFileContentAPIView.as_view(), name="samba_file_content"),
    path("file_stream/", SambaFileStreamAPIView.as_view(), name="samba_file_stream"),
    path("file_upload/", SambaFileUploadAPIView.as_view(), name="samba_file_upload"),
]
