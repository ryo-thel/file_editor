from rest_framework import generics
from .serializers import SambaFileSerializer
from smbprotocol.connection import Connection
from smbprotocol.file_info import FileInformationClass
from .models import SambaServer
from rest_framework import mixins, status
from rest_framework.response import Response
from .serializers import SambaFileContentSerializer
import base64
import os
from django.http import StreamingHttpResponse
from rest_framework.parsers import FileUploadParser


class SambaFileListAPIView(generics.ListAPIView):
    serializer_class = SambaFileSerializer

    def get_samba_connection(self):
        server = SambaServer.objects.first()  # あなたの Samba サーバー情報を取得
        conn = Connection(
            server.address, server.username, server.password, server.domain
        )
        conn.connect()
        return conn

    def get_queryset(self):
        server = SambaServer.objects.first()  # あなたの Samba サーバー情報を取得
        conn = self.get_samba_connection()
        # Samba サーバーからファイル情報を取得
        file_information = conn.list(server.share_name, "*")
        file_list = []

        for info in file_information:
            file_info = conn.query_file_info(
                info, FileInformationClass.FileAllInformation
            )
            file_list.append(
                {
                    "name": file_info.file_name,
                    "is_directory": file_info.end_of_file == 0,
                }
            )

        return file_list


class SambaFileContentAPIView(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView
):
    serializer_class = SambaFileContentSerializer

    def get_samba_connection(self):
        server = SambaServer.objects.first()  # あなたの Samba サーバー情報を取得
        conn = Connection(
            server.address, server.username, server.password, server.domain
        )
        conn.connect()
        return conn

    def get_object(self, conn, file_path):
        server = SambaServer.objects.first()
        with conn.open(server.share_name, file_path, mode="rb") as remote_file:
            content = remote_file.read()
        return content.decode("utf-8")

    def put_object(self, conn, file_path, content):
        server = SambaServer.objects.first()
        with conn.open(server.share_name, file_path, mode="wb") as remote_file:
            remote_file.write(content.encode("utf-8"))

    def get(self, request, *args, **kwargs):
        file_path = request.query_params.get("path")
        if not file_path:
            return Response(
                {"detail": "File path is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        conn = self.get_samba_connection()
        content = self.get_object(conn, file_path)
        encoded_content = base64.b64encode(content).decode("utf-8")
        serializer = self.get_serializer({"content": encoded_content})
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        file_path = request.query_params.get("path")
        if not file_path:
            return Response(
                {"detail": "File path is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        content = serializer.validated_data["content"]
        decoded_content = base64.b64decode(content.encode("utf-8"))

        conn = self.get_samba_connection()
        self.put_object(conn, file_path, decoded_content)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SambaFileStreamAPIView(generics.GenericAPIView):
    def get_samba_connection(self, server):
        conn = Connection(
            server.address, server.username, server.password, server.domain
        )
        conn.connect()
        return conn

    def file_iterator(self, conn, file_path, chunk_size=8192):
        server = SambaServer.objects.first()
        with conn.open(server.share_name, file_path, mode="rb") as remote_file:
            while True:
                chunk = remote_file.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    def get(self, request, *args, **kwargs):
        file_path = request.query_params.get("path")
        if not file_path:
            return Response(
                {"detail": "File path is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        server = SambaServer.objects.first()
        conn = self.get_samba_connection(server)

        response = StreamingHttpResponse(self.file_iterator(conn, file_path))
        response[
            "Content-Disposition"
        ] = f'attachment; filename="{os.path.basename(file_path)}"'
        return response


class SambaFileUploadAPIView(generics.GenericAPIView):
    parser_classes = [FileUploadParser]

    def get_samba_connection(self, server):
        server = SambaServer.objects.first()
        conn = Connection(
            server.address, server.username, server.password, server.domain
        )
        conn.connect()
        return conn

    def put(self, request, *args, **kwargs):
        file_path = request.query_params.get("path")
        if not file_path:
            return Response(
                {"detail": "File path is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        uploaded_file = request.data["file"]
        server = SambaServer.objects.first()
        conn = self.get_samba_connection(server)

        with conn.open(server.share_name, file_path, mode="wb") as remote_file:
            for chunk in uploaded_file.chunks():
                remote_file.write(chunk)

        return Response(status=status.HTTP_204_NO_CONTENT)
