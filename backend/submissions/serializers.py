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


class SubmissionRunSerializer(serializers.Serializer):
    problem = serializers.IntegerField()
    source_code = serializers.CharField()
    language = serializers.CharField(default="cpp")
    language_standard = serializers.ChoiceField(
        choices=Submission.LanguageStandard.choices,
        default=Submission.LanguageStandard.CPP14,
    )

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
