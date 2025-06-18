import type { Collection, Db } from "mongodb";

export interface SystemPrompt {
	_id: "system_prompt";
	prompt: string;
	updatedAt: Date;
	createdAt: Date;
}

export const getSystemPromptCollection = (db: Db): Collection<SystemPrompt> =>
	db.collection<SystemPrompt>("system_prompts");
