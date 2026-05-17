import subprocess
import tempfile
from pathlib import Path
import os

from django.conf import settings

from .models import Submission


class CppJudgeService:
    def judge(self, submission: Submission) -> Submission:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            source = workspace / "main.cpp"
            binary = workspace / ("main.exe" if os.name == "nt" else "main")
            source.write_text(submission.source_code, encoding="utf-8")

            compile_result = subprocess.run(
                [
                    settings.CPP_COMPILER,
                    f"-std={submission.language_standard}",
                    "-O2",
                    str(source),
                    "-o",
                    str(binary),
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if compile_result.returncode != 0:
                return self._finish(submission, Submission.Status.COMPILE_ERROR, compile_result.stderr)

            for case in submission.problem.test_cases.all():
                try:
                    run_result = subprocess.run(
                        [str(binary)],
                        input=case.input_data,
                        capture_output=True,
                        text=True,
                        timeout=settings.JUDGE_TIME_LIMIT_SECONDS,
                    )
                except subprocess.TimeoutExpired:
                    return self._finish(submission, Submission.Status.TIME_LIMIT_EXCEEDED, "执行超时")

                if run_result.returncode != 0:
                    return self._finish(submission, Submission.Status.RUNTIME_ERROR, run_result.stderr)

                if self._normalize(run_result.stdout) != self._normalize(case.output_data):
                    return self._finish(submission, Submission.Status.WRONG_ANSWER, "输出与标准答案不一致")

        return self._finish(submission, Submission.Status.ACCEPTED, "Accepted")

    @staticmethod
    def _normalize(value: str) -> str:
        return "\n".join(line.rstrip() for line in value.strip().splitlines())

    @staticmethod
    def _finish(submission: Submission, status: str, detail: str) -> Submission:
        submission.status = status
        submission.detail = detail
        submission.save(update_fields=["status", "detail"])
        return submission
