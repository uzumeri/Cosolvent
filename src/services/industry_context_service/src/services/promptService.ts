import { defaultPrompt } from "@/utils/defultPrompt";
import type { Redis } from "ioredis";
import * as repo from "@/repositories/promptRepo";

const SYSTEM_PROMPT_KEY = "system_prompt";

export class PromptService {
	constructor(
		private redis: Redis,
	) {}

	async getPrompt(): Promise<string> {
		if (this.redis) {
			const cached = await this.redis.get(SYSTEM_PROMPT_KEY);
			if (cached) return cached;
		}

		const prompt = (await repo.getPrompt()) ?? defaultPrompt;

		if (this.redis) {
			await this.redis.set(SYSTEM_PROMPT_KEY, prompt, "EX", 3600);
		}

		return prompt;
	}

	async setPrompt(newPrompt: string) {
		await repo.setPrompt(newPrompt);

		if (this.redis) await this.redis.del("system_prompt");
	}
}
