export type SampleCase = {
  id: number;
  input_data: string;
  output_data: string;
};

export type Problem = {
  id: number;
  title: string;
  description: string;
  input_description: string;
  output_description: string;
  difficulty: string;
  sample_cases: SampleCase[];
};

export type Submission = {
  id: number;
  language_standard: "c++11" | "c++14" | "c++17";
  status: string;
  detail: string;
};

export type RunCaseResult = {
  status: string;
  input_data: string;
  expected_output: string;
  actual_output: string;
  detail: string;
  diff: string;
};

export type RunResult = {
  status: string;
  detail: string;
  cases: RunCaseResult[];
};
