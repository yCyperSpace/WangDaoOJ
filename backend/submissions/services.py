import os
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from difflib import unified_diff
from pathlib import Path

from django.conf import settings

from .models import Submission


@dataclass
class CaseExecutionResult:
    status: str
    input_data: str
    expected_output: str
    actual_output: str
    detail: str
    diff: str


class CppJudgeService:
    def judge(self, submission: Submission) -> Submission:
        result = self.run_cases(
            source_code=submission.source_code,
            language_standard=submission.language_standard,
            cases=submission.problem.test_cases.all(),
        )
        return self._finish(submission, result["status"], result["detail"])

    def run_samples(self, *, source_code: str, language_standard: str, cases) -> dict:
        return self.run_cases(
            source_code=source_code,
            language_standard=language_standard,
            cases=cases,
        )

    def run_cases(self, *, source_code: str, language_standard: str, cases) -> dict:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            source = workspace / "main.cpp"
            binary = workspace / ("main.exe" if os.name == "nt" else "main")
            source.write_text(source_code, encoding="utf-8")

            compile_result = subprocess.run(
                [
                    settings.CPP_COMPILER,
                    f"-std={language_standard}",
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
                return {
                    "status": Submission.Status.COMPILE_ERROR,
                    "detail": compile_result.stderr,
                    "cases": [],
                }

            case_results = []
            overall_status = Submission.Status.ACCEPTED
            for case in cases:
                case_result = self._run_one_case(binary, case)
                case_results.append(asdict(case_result))
                if (
                    overall_status == Submission.Status.ACCEPTED
                    and case_result.status != Submission.Status.ACCEPTED
                ):
                    overall_status = case_result.status

        return {
            "status": overall_status,
            "detail": "Accepted" if overall_status == Submission.Status.ACCEPTED else "存在未通过样例",
            "cases": case_results,
        }

    def _run_one_case(self, binary: Path, case) -> CaseExecutionResult:
        try:
            run_result = subprocess.run(
                [str(binary)],
                input=case.input_data,
                capture_output=True,
                text=True,
                timeout=settings.JUDGE_TIME_LIMIT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            return CaseExecutionResult(
                status=Submission.Status.TIME_LIMIT_EXCEEDED,
                input_data=case.input_data,
                expected_output=case.output_data,
                actual_output="",
                detail="执行超时",
                diff="",
            )

        if run_result.returncode != 0:
            return CaseExecutionResult(
                status=Submission.Status.RUNTIME_ERROR,
                input_data=case.input_data,
                expected_output=case.output_data,
                actual_output=run_result.stdout,
                detail=run_result.stderr,
                diff="",
            )

        expected = self._normalize(case.output_data)
        actual = self._normalize(run_result.stdout)
        if actual == expected:
            return CaseExecutionResult(
                status=Submission.Status.ACCEPTED,
                input_data=case.input_data,
                expected_output=case.output_data,
                actual_output=run_result.stdout,
                detail="Accepted",
                diff="",
            )

        return CaseExecutionResult(
            status=Submission.Status.WRONG_ANSWER,
            input_data=case.input_data,
            expected_output=case.output_data,
            actual_output=run_result.stdout,
            detail="输出与标准答案不一致",
            diff=self._build_diff(case.output_data, run_result.stdout),
        )

    @staticmethod
    def _normalize(value: str) -> str:
        return "\n".join(line.rstrip() for line in value.strip().splitlines())

    @staticmethod
    def _finish(submission: Submission, status: str, detail: str) -> Submission:
        submission.status = status
        submission.detail = detail
        submission.save(update_fields=["status", "detail"])
        return submission

    @staticmethod
    def _build_diff(expected_output: str, actual_output: str) -> str:
        return "\n".join(
            unified_diff(
                expected_output.splitlines(),
                actual_output.splitlines(),
                fromfile="expected",
                tofile="actual",
                lineterm="",
            )
        )
