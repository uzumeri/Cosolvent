import { newOpenAIChatModel } from "@/factory/llms";
import { newLangGraphMemory } from "@/factory/memorys";
import { trimMessages } from "@langchain/core/messages";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import {
	START,
	END,
	MessagesAnnotation,
	StateGraph,
} from "@langchain/langgraph";

const memory = newLangGraphMemory();
const model = newOpenAIChatModel({
	modelName: "gpt-4",
});

// trim messages to manage overflow
const trimmer = trimMessages({
	maxTokens: 1000,
	strategy: "last",
	tokenCounter: (msgs) => msgs.length,
	includeSystem: true,
	allowPartial: true,
	startOn: "human",
});

const promptTemplate = ChatPromptTemplate.fromMessages([
	[
		"system",
		"You are a helpful assistant. Answer all questions to the best of your ability.",
	],
	["placeholder", "{messages}"],
]);

const callModel = async (state: typeof MessagesAnnotation.State) => {
	const trimmedMessage = await trimmer.invoke(state.messages);
	const prompt = await promptTemplate.invoke({
		messages: trimmedMessage,
	});
	const response = await model.invoke(prompt);
	return { messages: [response] };
};

// langGraph workflow
// START --> model --> END
const workflow = new StateGraph(MessagesAnnotation)
	.addNode("model", callModel)
	.addEdge(START, "model")
	.addEdge("model", END);

const chatApp = workflow.compile({ checkpointer: memory });

export default chatApp;
