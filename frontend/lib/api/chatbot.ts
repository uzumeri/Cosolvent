import type { ChatBotQuery, ChatBotResponse } from "@/types/chatbot";
import axiosInstance from "./axios";

const askChatBot = async ({
	threadId,
	question,
}: ChatBotQuery): Promise<ChatBotResponse> => {
	const response = await axiosInstance.post("/query", {
		threadId,
		question,
	});

	return response.data;
};

export { askChatBot };
