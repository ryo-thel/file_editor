from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from .models import SambaServer

class SambaServerTestCase(TestCase):

    def setUp(self):
        SambaServer.objects.create(
            address='192.168.1.100',
            username='user',
            password='password',
            domain='example.com',
            share_name='shared'
        )

class SambaFileListAPIViewTestCase(SambaServerTestCase):

    def test_samba_file_list(self):
        client = APIClient()
        url = reverse('samba_file_list')  # URLを適切に設定してください
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        # 必要に応じて、期待するファイルリストと実際のファイルリストを比較

class SambaFileContentAPIViewTestCase(SambaServerTestCase):

    def test_samba_file_content(self):
        client = APIClient()
        url = reverse('samba_file_content')  # URLを適切に設定してください
        response = client.get(url, {'path': 'path/to/file.txt'})
        self.assertEqual(response.status_code, 200)
        # 必要に応じて、期待するファイル内容と実際のファイル内容を比較

class SambaFileStreamAPIViewTestCase(SambaServerTestCase):

    def test_samba_file_stream(self):
        client = APIClient()
        url = reverse('samba_file_stream')  # URLを適切に設定してください
        response = client.get(url, {'path': 'path/to/file.txt'})
        self.assertEqual(response.status_code, 200)
        # 必要に応じて、期待するファイルのバイナリデータと実際のバイナリデータを比較

class SambaFileUploadAPIViewTestCase(SambaServerTestCase):

    def test_samba_file_upload(self):
        client = APIClient()
        url = reverse('samba_file_upload')  # URLを適切に設定してください
        with open('path/to/local/file.txt', 'rb') as f:
            response = client.put(url, {'file': f}, format='multipart', QUERY_STRING='path=path/to/remote/file.txt')
        self.assertEqual(response.status_code, 204)
        # 必要に応じて、アップロードされたファイルの内容を確認

