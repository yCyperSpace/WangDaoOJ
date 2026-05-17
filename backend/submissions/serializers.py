from rest_framework import serializers

from .models import Submission


class SubmissionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ["id", "problem", "source_code", "language"]

    def validate_language(self, value):
        if value != "cpp":
            raise serializers.ValidationError("目前只支持 cpp")
        return value


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ["id", "problem", "source_code", "language", "status", "detail", "created_at"]

