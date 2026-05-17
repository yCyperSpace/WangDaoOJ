from dataclasses import dataclass
from typing import Protocol

import requests
from django.conf import settings

from .models import Problem


class ReferenceSolutionGenerator(Protocol):
    def generate(self, problem: Problem) -> str: ...


@dataclass
class DeepSeekReferenceSolutionGenerator:
    api_key: str
    base_url: str
    model: str

    def generate(self, problem: Problem) -> str:
        if not self.api_key:
            raise RuntimeError("DEEPSEEK_API_KEY is not configured")

        prompt = (
            "你是一名严谨的算法教练。请为下面题目输出可直接提交的 C++17 标准答案，"
            "只返回代码，不要解释。\n\n"
            f"题目：{problem.title}\n"
            f"描述：{problem.description}\n"
            f"输入说明：{problem.input_description}\n"
            f"输出说明：{problem.output_description}\n"
        )
        response = requests.post(
            f"{self.base_url.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


def build_reference_solution_generator() -> ReferenceSolutionGenerator:
    return DeepSeekReferenceSolutionGenerator(
        api_key=settings.DEEPSEEK_API_KEY,
        base_url=settings.DEEPSEEK_BASE_URL,
        model=settings.DEEPSEEK_MODEL,
    )

