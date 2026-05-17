from rest_framework import serializers

from .models import Submission


class SubmissionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ["id", "problem", "source_code", "language", "language_standard"]

    def validate_language(self, value):
        if value != "cpp":
            raise serializers.ValidationError("目前只支持 cpp")
        return value


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = [
            "id",
            "problem",
            "source_code",
            "language",
            "language_standard",
            "status",
            "detail",
            "created_at",
        ]
