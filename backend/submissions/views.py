from rest_framework import mixins, viewsets
from rest_framework.response import Response

from .models import Submission
from .serializers import SubmissionCreateSerializer, SubmissionSerializer
from .services import CppJudgeService


class SubmissionViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Submission.objects.select_related("problem").all()

    def get_serializer_class(self):
        if self.action == "create":
            return SubmissionCreateSerializer
        return SubmissionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        submission = serializer.save()
        submission = CppJudgeService().judge(submission)
        return Response(SubmissionSerializer(submission).data)

