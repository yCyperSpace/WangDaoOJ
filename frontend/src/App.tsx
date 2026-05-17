import Editor from "@monaco-editor/react";
import type { editor as MonacoEditor, Range } from "monaco-editor";
import { Code2, Play, Upload } from "lucide-react";
import { FormEvent, PointerEvent as ReactPointerEvent, useEffect, useMemo, useRef, useState } from "react";

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
  const [activeCaseIndex, setActiveCaseIndex] = useState(0);
  const [resultHeight, setResultHeight] = useState(260);
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

  const activeCase = runResult?.cases[activeCaseIndex] ?? null;

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

  function handleResizeStart(event: ReactPointerEvent<HTMLDivElement>) {
    event.preventDefault();
    const startY = event.clientY;
    const startHeight = resultHeight;

    function handlePointerMove(moveEvent: PointerEvent) {
      const nextHeight = Math.min(520, Math.max(180, startHeight + startY - moveEvent.clientY));
      setResultHeight(nextHeight);
    }

    function handlePointerUp() {
      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("pointerup", handlePointerUp);
    }

    window.addEventListener("pointermove", handlePointerMove);
    window.addEventListener("pointerup", handlePointerUp);
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
      setActiveCaseIndex(0);
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
            height={`calc(100vh - ${resultHeight + 112}px)`}
            defaultLanguage="cpp"
            theme="vs-dark"
            value={code}
            onMount={handleEditorMount}
            onChange={(value) => setCode(value ?? "")}
            options={{ minimap: { enabled: false }, fontSize: 14 }}
          />
          <div
            className="result-resizer"
            onPointerDown={handleResizeStart}
            role="separator"
            aria-orientation="horizontal"
            aria-label="调整结果区高度"
          />
          <footer className="result-panel" style={{ height: resultHeight }}>
            {runResult ? (
              <>
                <div className="result-heading">
                  <div>
                    <strong className={`status ${runResult.status}`}>{runResult.status}</strong>
                    <span>{runResult.detail}</span>
                  </div>
                  <div className="case-tabs">
                    {runResult.cases.map((caseResult, index) => (
                      <button
                        className={index === activeCaseIndex ? "active" : ""}
                        key={`${caseResult.status}-${index}`}
                        onClick={() => setActiveCaseIndex(index)}
                      >
                        Case {index + 1}
                      </button>
                    ))}
                  </div>
                </div>
                {activeCase && (
                  <article className="case-console">
                    <div className="console-summary">
                      <strong className={`status ${activeCase.status}`}>{activeCase.status}</strong>
                      <span>{activeCase.detail}</span>
                    </div>
                    <div className="io-grid">
                      <section>
                        <label>输入</label>
                        <pre>{activeCase.input_data}</pre>
                      </section>
                      <section>
                        <label>期望输出</label>
                        <pre>{activeCase.expected_output}</pre>
                      </section>
                      <section>
                        <label>实际输出</label>
                        <pre>{activeCase.actual_output || "(无输出)"}</pre>
                      </section>
                    </div>
                    {activeCase.diff && (
                      <section className="diff-block">
                        <label>差异</label>
                        <pre>{activeCase.diff}</pre>
                      </section>
                    )}
                  </article>
                )}
              </>
            ) : (
              <div className="result-heading">
                <div>
                  <strong className={`status ${submission?.status ?? ""}`}>
                    {submission?.status ?? "尚未运行"}
                  </strong>
                  <span>{submission?.detail ?? "运行样例可查看期望输出、实际输出和差异"}</span>
                </div>
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
