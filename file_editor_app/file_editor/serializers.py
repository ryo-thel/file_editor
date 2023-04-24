from rest_framework import serializers


class SambaFileSerializer(serializers.Serializer):
    name = serializers.CharField()
    is_directory = serializers.BooleanField()
    
class SambaFileContentSerializer(serializers.Serializer):
    content = serializers.CharField()
