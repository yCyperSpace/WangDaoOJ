import Editor from "@monaco-editor/react";
import { Code2, Play, Upload } from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";

import { api } from "./api";
import type { Problem, Submission } from "./types";

const starterCode = `#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    return 0;
}
`;

export function App() {
  const [problems, setProblems] = useState<Problem[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [code, setCode] = useState(starterCode);
  const [submission, setSubmission] = useState<Submission | null>(null);
  const [uploadOpen, setUploadOpen] = useState(false);

  useEffect(() => {
    api.get<Problem[]>("/problems/").then(({ data }) => {
      setProblems(data);
      setSelectedId(data[0]?.id ?? null);
    });
  }, []);

  const selectedProblem = useMemo(
    () => problems.find((problem) => problem.id === selectedId) ?? null,
    [problems, selectedId],
  );

  async function handleSubmit() {
    if (!selectedProblem) return;
    const { data } = await api.post<Submission>("/submissions/", {
      problem: selectedProblem.id,
      source_code: code,
      language: "cpp",
    });
    setSubmission(data);
  }

  async function handleUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const { data } = await api.post<Problem>("/problems/upload/", {
      title: form.get("title"),
      description: form.get("description"),
      input_description: form.get("input_description"),
      output_description: form.get("output_description"),
      samples: [
        {
          input_data: form.get("sample_input"),
          output_data: form.get("sample_output"),
        },
      ],
    });
    setProblems((current) => [data, ...current]);
    setSelectedId(data.id);
    setUploadOpen(false);
  }

  return (
    <main className="shell">
      <header className="topbar">
        <div className="brand">
          <Code2 size={20} />
          <span>Online Judge</span>
        </div>
        <button className="ghost" onClick={() => setUploadOpen(true)}>
          <Upload size={16} />
          上传题目
        </button>
      </header>

      <section className="workspace">
        <aside className="problem-list">
          {problems.map((problem) => (
            <button
              className={problem.id === selectedId ? "active" : ""}
              key={problem.id}
              onClick={() => setSelectedId(problem.id)}
            >
              <strong>{problem.title}</strong>
              <span>{problem.difficulty}</span>
            </button>
          ))}
        </aside>

        <article className="problem-pane">
          {selectedProblem ? (
            <>
              <h1>{selectedProblem.title}</h1>
              <p>{selectedProblem.description}</p>
              <h2>输入说明</h2>
              <p>{selectedProblem.input_description || "按题意输入"}</p>
              <h2>输出说明</h2>
              <p>{selectedProblem.output_description || "按题意输出"}</p>
              <h2>样例</h2>
              {selectedProblem.sample_cases.map((sample) => (
                <div className="sample" key={sample.id}>
                  <label>输入</label>
                  <pre>{sample.input_data}</pre>
                  <label>输出</label>
                  <pre>{sample.output_data}</pre>
                </div>
              ))}
            </>
          ) : (
            <p>暂无题目</p>
          )}
        </article>

        <section className="editor-pane">
          <div className="editor-toolbar">
            <span>C++17</span>
            <button onClick={handleSubmit}>
              <Play size={16} />
              提交
            </button>
          </div>
          <Editor
            height="calc(100vh - 170px)"
            defaultLanguage="cpp"
            theme="vs-dark"
            value={code}
            onChange={(value) => setCode(value ?? "")}
            options={{ minimap: { enabled: false }, fontSize: 14 }}
          />
          <footer className="result-bar">
            <strong>{submission?.status ?? "尚未提交"}</strong>
            <span>{submission?.detail ?? "提交后会在这里显示判题结果"}</span>
          </footer>
        </section>
      </section>

      {uploadOpen && (
        <div className="modal-backdrop">
          <form className="modal" onSubmit={handleUpload}>
            <h2>上传题目</h2>
            <input name="title" placeholder="题目标题" required />
            <textarea name="description" placeholder="题目描述" required />
            <textarea name="input_description" placeholder="输入说明" />
            <textarea name="output_description" placeholder="输出说明" />
            <textarea name="sample_input" placeholder="样例输入" required />
            <textarea name="sample_output" placeholder="样例输出" required />
            <div className="actions">
              <button type="button" className="ghost" onClick={() => setUploadOpen(false)}>
                取消
              </button>
              <button type="submit">创建</button>
            </div>
          </form>
        </div>
      )}
    </main>
  );
}

