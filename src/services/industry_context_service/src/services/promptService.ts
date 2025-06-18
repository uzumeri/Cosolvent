import { getSystemPromptCollection } from "@/models/systemPrompt";
import { defaultPrompt } from "@/utils/defultPrompt";
import type { Redis } from "ioredis";
import type { Db } from "mongodb";

const SYSTEM_PROMPT_KEY = "system_prompt";

export class PromptService {
	constructor(
		private db: Db,
		private redis?: Redis,
	) {}

	async getPrompt(): Promise<string> {
		if (this.redis) {
			const cached = await this.redis.get(SYSTEM_PROMPT_KEY);
			if (cached) return cached;
		}

		const col = getSystemPromptCollection(this.db);
		const doc = await col.findOne({ _id: SYSTEM_PROMPT_KEY });
		const prompt = doc?.prompt ?? defaultPrompt;

		if (this.redis) {
			await this.redis.set(SYSTEM_PROMPT_KEY, prompt, "EX", 3600);
		}

		return prompt;
	}

	async setPrompt(newPrompt: string) {
		const col = getSystemPromptCollection(this.db);

		await col.updateOne(
			{ _id: SYSTEM_PROMPT_KEY },
			{
				$set: { prompt: newPrompt, updatedAt: new Date() },
				$setOnInsert: { createdAt: new Date() },
			},
			{ upsert: true },
		);

		if (this.redis) await this.redis.del("system_prompt");
	}
}
