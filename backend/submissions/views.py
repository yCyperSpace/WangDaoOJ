from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from problems.models import Problem

from .models import Submission
from .serializers import SubmissionCreateSerializer, SubmissionRunSerializer, SubmissionSerializer
from .services import CppJudgeService


class SubmissionViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Submission.objects.select_related("problem").all()

    def get_serializer_class(self):
        if self.action == "create":
            return SubmissionCreateSerializer
        if self.action == "run":
            return SubmissionRunSerializer
        return SubmissionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        submission = serializer.save()
        submission = CppJudgeService().judge(submission)
        return Response(SubmissionSerializer(submission).data)

    @action(detail=False, methods=["post"])
    def run(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        problem = get_object_or_404(Problem, pk=serializer.validated_data["problem"])
        result = CppJudgeService().run_samples(
            source_code=serializer.validated_data["source_code"],
            language_standard=serializer.validated_data["language_standard"],
            cases=problem.sample_cases.all(),
        )
        return Response(result)
