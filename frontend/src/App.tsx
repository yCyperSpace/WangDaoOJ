import Editor from "@monaco-editor/react";
import type { editor as MonacoEditor, Range } from "monaco-editor";
import { Code2, Play, Upload } from "lucide-react";
import { FormEvent, useEffect, useMemo, useRef, useState } from "react";

import { api } from "./api";
import type { Problem, RunResult, Submission } from "./types";

const starterCode = `#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    return 0;
}
`;

type MonacoInstance = typeof import("monaco-editor");

export function App() {
  const [problems, setProblems] = useState<Problem[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [code, setCode] = useState(starterCode);
  const [languageStandard, setLanguageStandard] = useState<"c++11" | "c++14" | "c++17">("c++14");
  const [submission, setSubmission] = useState<Submission | null>(null);
  const [runResult, setRunResult] = useState<RunResult | null>(null);
  const [busyAction, setBusyAction] = useState<"run" | "submit" | "upload" | null>(null);
  const [uploadOpen, setUploadOpen] = useState(false);
  const editorRef = useRef<MonacoEditor.IStandaloneCodeEditor | null>(null);
  const monacoRef = useRef<MonacoInstance | null>(null);
  const decorationIds = useRef<string[]>([]);

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

  function updateCppDecorations() {
    const editor = editorRef.current;
    const monaco = monacoRef.current;
    if (!editor || !monaco) return;

    const model = editor.getModel();
    if (!model) return;
    const matches = model.findMatches("\\b(cin|cout|cerr|clog|endl)\\b", false, true, false, null, true);
    decorationIds.current = editor.deltaDecorations(
      decorationIds.current,
      matches.map((match) => ({
        range: match.range as Range,
        options: { inlineClassName: "cpp-stream-token" },
      })),
    );
  }

  function handleEditorMount(editor: MonacoEditor.IStandaloneCodeEditor, monaco: MonacoInstance) {
    editorRef.current = editor;
    monacoRef.current = monaco;
    updateCppDecorations();
    editor.onDidChangeModelContent(updateCppDecorations);
  }

  async function handleRun() {
    if (!selectedProblem) return;
    setBusyAction("run");
    try {
      const { data } = await api.post<RunResult>("/submissions/run/", {
        problem: selectedProblem.id,
        source_code: code,
        language: "cpp",
        language_standard: languageStandard,
      });
      setRunResult(data);
      setSubmission(null);
    } finally {
      setBusyAction(null);
    }
  }

  async function handleSubmit() {
    if (!selectedProblem) return;
    setBusyAction("submit");
    try {
      const { data } = await api.post<Submission>("/submissions/", {
        problem: selectedProblem.id,
        source_code: code,
        language: "cpp",
        language_standard: languageStandard,
      });
      setSubmission(data);
      setRunResult(null);
    } finally {
      setBusyAction(null);
    }
  }

  async function handleUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setBusyAction("upload");
    try {
      const { data } = await api.post<Problem>("/problems/upload/", {
        statement: form.get("statement"),
      });
      setProblems((current) => [data, ...current]);
      setSelectedId(data.id);
      setUploadOpen(false);
    } finally {
      setBusyAction(null);
    }
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
            <select
              aria-label="C++ 标准"
              value={languageStandard}
              onChange={(event) =>
                setLanguageStandard(event.target.value as "c++11" | "c++14" | "c++17")
              }
            >
              <option value="c++11">C++11</option>
              <option value="c++14">C++14</option>
              <option value="c++17">C++17</option>
            </select>
            <div className="toolbar-actions">
              <button className="secondary" onClick={handleRun} disabled={busyAction !== null}>
                <Play size={16} />
                {busyAction === "run" ? "运行中" : "运行"}
              </button>
              <button onClick={handleSubmit} disabled={busyAction !== null}>
                <Play size={16} />
                {busyAction === "submit" ? "提交中" : "提交"}
              </button>
            </div>
          </div>
          <Editor
            height="calc(100vh - 260px)"
            defaultLanguage="cpp"
            theme="vs-dark"
            value={code}
            onMount={handleEditorMount}
            onChange={(value) => setCode(value ?? "")}
            options={{ minimap: { enabled: false }, fontSize: 14 }}
          />
          <footer className="result-panel">
            {runResult ? (
              <>
                <div className="result-heading">
                  <strong>{runResult.status}</strong>
                  <span>{runResult.detail}</span>
                </div>
                <div className="case-grid">
                  {runResult.cases.map((caseResult, index) => (
                    <article className="case-card" key={`${caseResult.status}-${index}`}>
                      <header>
                        <strong>样例 {index + 1}</strong>
                        <span>{caseResult.status}</span>
                      </header>
                      <label>输入</label>
                      <pre>{caseResult.input_data}</pre>
                      <label>期望输出</label>
                      <pre>{caseResult.expected_output}</pre>
                      <label>实际输出</label>
                      <pre>{caseResult.actual_output || "(无输出)"}</pre>
                      {caseResult.diff && (
                        <>
                          <label>差异</label>
                          <pre className="diff">{caseResult.diff}</pre>
                        </>
                      )}
                      {caseResult.detail && <p>{caseResult.detail}</p>}
                    </article>
                  ))}
                </div>
              </>
            ) : (
              <div className="result-heading">
                <strong>{submission?.status ?? "尚未运行"}</strong>
                <span>{submission?.detail ?? "运行样例可查看期望输出、实际输出和差异"}</span>
              </div>
            )}
          </footer>
        </section>
      </section>

      {uploadOpen && (
        <div className="modal-backdrop">
          <form className="modal" onSubmit={handleUpload}>
            <h2>上传题目</h2>
            <textarea
              name="statement"
              placeholder="粘贴完整题面，DeepSeek 会自动生成题目结构、样例、隐藏测试点和参考解"
              required
            />
            <div className="actions">
              <button type="button" className="ghost" onClick={() => setUploadOpen(false)}>
                取消
              </button>
              <button type="submit" disabled={busyAction !== null}>
                {busyAction === "upload" ? "生成中" : "创建"}
              </button>
            </div>
          </form>
        </div>
      )}
    </main>
  );
}
