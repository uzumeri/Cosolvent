import env from "@/config/env";
import { newOpenAIEmbedding } from "@/factory/embeddings";
import { newOpenAIChatModel } from "@/factory/llms";
import { newLangGraphMemory } from "@/factory/memorys";
import { newVectorStore } from "@/factory/vectorStores";
import createRetrieveTool from "@/utils/retrieve";
import {
	AIMessage,
	HumanMessage,
	ToolMessage,
	trimMessages,
} from "@langchain/core/messages";
import type { SystemMessage } from "@langchain/core/messages";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import {
	END,
	MessagesAnnotation,
	START,
	StateGraph,
} from "@langchain/langgraph";
import { ToolNode, toolsCondition } from "@langchain/langgraph/prebuilt";

// setup shared resources
const memory = newLangGraphMemory();
const embedding = newOpenAIEmbedding({
	modelName: "text-embedding-3-small",
});
const vectorIndex = await newVectorStore(embedding, "embeddings");
const model = newOpenAIChatModel({
	modelName: "gpt-4o",
});
const retrieveTool = createRetrieveTool(vectorIndex);

// trim messages to manage overflow
const trimmer = trimMessages({
	maxTokens: 1000,
	strategy: "last",
	tokenCounter: (msgs: any[]) => msgs.length,
	includeSystem: true,
	allowPartial: true,
	startOn: "human",
});

const newChatAgent = async ({ systemPrompt }: { systemPrompt: string }) => {
	const promptTemplate = ChatPromptTemplate.fromMessages([
		["system", `${systemPrompt}`],
		["placeholder", "{messages}"],
	]);

	async function preparePrompt(
		context: string,
		messages: (AIMessage | HumanMessage | SystemMessage)[],
	) {
		const trimmedMessages = await trimmer.invoke(messages);
		return promptTemplate.invoke({
			context,
			messages: trimmedMessages,
		});
	}

	const callModel = async (state: typeof MessagesAnnotation.State) => {
		const toolMessages = state.messages.filter(
			(msg) => msg.getType() === "tool",
		);
		const context = toolMessages.map((msg) => msg.content).join("\n\n");
		const prompt = await preparePrompt(context, state.messages);
		const llmWithTool = model.bindTools([retrieveTool]);
		const response = await llmWithTool.invoke(prompt);
		return { messages: [response] };
	};

	async function generateResponse(state: typeof MessagesAnnotation.State) {
		const recentToolMessages = [];
		for (let i = state.messages.length - 1; i >= 0; i--) {
			const message = state.messages[i];
			if (message instanceof ToolMessage) {
				recentToolMessages.push(message);
			} else {
				break;
			}
		}
		const toolMessages = recentToolMessages.reverse();
		const context = toolMessages.map((doc) => doc.content).join("\n");

		const conversationMessages = state.messages.filter(
			(message) =>
				message instanceof HumanMessage ||
				(message instanceof AIMessage && message.tool_calls?.length === 0),
		);

		const prompt = await preparePrompt(context, conversationMessages);

		// Generate response
		const response = await model.invoke(prompt);
		return { messages: [response] };
	}

	// langGraph workflow
	// START --> model --> tools --> generate --> END
	const workflow = new StateGraph(MessagesAnnotation)
		.addNode("model", callModel)
		.addNode("tools", new ToolNode([retrieveTool]))
		.addNode("generate", generateResponse)
		.addEdge(START, "model")
		.addConditionalEdges("model", toolsCondition, {
			[END]: "generate",
			tools: "tools",
		})
		.addEdge("tools", "generate")
		.addEdge("generate", END);

	return workflow.compile({ checkpointer: memory });
};

export default newChatAgent;
