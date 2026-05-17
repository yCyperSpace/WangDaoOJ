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
  status: string;
  detail: string;
};

