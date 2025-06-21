import type { BaseApiReponse } from "./reponse";

export type ChatBotResponse = BaseApiReponse<{
	threadId: string;
	question: string;
	aiResponse: string;
}>;

export type ChatBotQuery = {
	threadId: string;
	question: string;
};
