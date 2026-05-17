import json
from dataclasses import dataclass
from typing import Protocol, TypedDict

import requests
from django.conf import settings


class GeneratedCase(TypedDict):
    input_data: str
    output_data: str


class GeneratedProblemPackage(TypedDict):
    title: str
    description: str
    input_description: str
    output_description: str
    difficulty: str
    reference_solution: str
    sample_cases: list[GeneratedCase]
    hidden_test_cases: list[GeneratedCase]


class ProblemPackageGenerator(Protocol):
    def generate(self, statement: str) -> GeneratedProblemPackage: ...


@dataclass
class DeepSeekProblemPackageGenerator:
    api_key: str
    base_url: str
    model: str

    def generate(self, statement: str) -> GeneratedProblemPackage:
        if not self.api_key:
            raise RuntimeError("DEEPSEEK_API_KEY is not configured")

        system_prompt = (
            "你是一名在线判题系统的出题助手。用户只会给出原始题面。"
            "请输出严格 JSON，用于直接创建题目、公开样例、隐藏测试点和 C++14 参考解。"
            "公开样例至少 2 组，隐藏测试点至少 5 组，并覆盖边界情况。"
            "不要输出 markdown，不要输出解释。"
            'JSON 格式示例：{"title":"两数之和","description":"...","input_description":"...",'
            '"output_description":"...","difficulty":"easy","reference_solution":"#include <bits/stdc++.h>...",'
            '"sample_cases":[{"input_data":"1 2\\n","output_data":"3\\n"}],'
            '"hidden_test_cases":[{"input_data":"0 0\\n","output_data":"0\\n"}]}'
        )
        response = requests.post(
            f"{self.base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"请根据下面题面输出 JSON：\n{statement}"},
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.1,
                "max_tokens": 4096,
                "thinking": {"type": "disabled"},
            },
            timeout=90,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        if not content:
            raise RuntimeError("DeepSeek returned empty content")
        return json.loads(content)


def build_problem_package_generator() -> ProblemPackageGenerator:
    return DeepSeekProblemPackageGenerator(
        api_key=settings.DEEPSEEK_API_KEY,
        base_url=settings.DEEPSEEK_BASE_URL,
        model=settings.DEEPSEEK_MODEL,
    )
