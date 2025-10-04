// Deprecated: use Postgres-backed repositories in repositories/promptRepo.ts instead of this file.
export type Db = unknown;
export interface Collection<T> {
  insertOne: (doc: T) => Promise<any>;
  updateOne: (filter: any, update: any) => Promise<any>;
  findOne: (filter: any) => Promise<T | null>;
}

export interface SystemPrompt {
  _id: "system_prompt";
  prompt: string;
  updatedAt: Date;
  createdAt: Date;
}

export const getSystemPromptCollection = (_db: Db): Collection<SystemPrompt> => {
  throw new Error("SystemPrompt collection removed. Use Postgres repositories instead.");
};
