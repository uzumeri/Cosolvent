import env from "@/config/env";
import { newOpenAIEmbedding } from "@/factory/embeddings";
import { newOpenAIChatModel } from "@/factory/llms";
import { newLangGraphMemory } from "@/factory/memorys";
import { newPineconeStore } from "@/factory/vectorStores";
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
	START,
	END,
	MessagesAnnotation,
	StateGraph,
} from "@langchain/langgraph";
import { ToolNode, toolsCondition } from "@langchain/langgraph/prebuilt";

const embedding = newOpenAIEmbedding({
	modelName: "text-embedding-3-small",
});
const pineconeIndex = await newPineconeStore(
	embedding,
	env.PINECONE_INDEX_NAME,
);

const memory = newLangGraphMemory();
const model = newOpenAIChatModel({
	modelName: "gpt-4o",
});
const retrieveTool = createRetrieveTool(pineconeIndex);

// trim messages to manage overflow
const trimmer = trimMessages({
	maxTokens: 1000,
	strategy: "last",
	tokenCounter: (msgs) => msgs.length,
	includeSystem: true,
	allowPartial: true,
	startOn: "human",
});

const basePromptTemplate = ChatPromptTemplate.fromMessages([
	[
		"system",
		`You are a helpful assistant that answers questions.
			Follow these rules:
			1. Make a tool call to get relevant context
			2. If context is provided, use it to answer
			3. If no context is relevant, say you don't know
			4. Be concise and factual
			5. For follow-up questions, maintain conversation context
		Context: {context}`,
	],
	["placeholder", "{messages}"],
]);

async function preparePrompt(
	context: string,
	messages: (AIMessage | HumanMessage | SystemMessage)[],
) {
	const trimmedMessages = await trimmer.invoke(messages);
	return basePromptTemplate.invoke({
		context,
		messages: trimmedMessages,
	});
}

const callModel = async (state: typeof MessagesAnnotation.State) => {
	// Get any tool messages (retrieved documents) from state
	const toolMessages = state.messages.filter((msg) => msg.getType() === "tool");
	const context = toolMessages.map((msg) => msg.content).join("\n\n");

	const prompt = await preparePrompt(context, state.messages);
	const llmWithTool = model.bindTools([retrieveTool]);
	const response = await llmWithTool.invoke(prompt);
	return { messages: [response] };
};

async function generateResponse(state: typeof MessagesAnnotation.State) {
	// Get tool messages (retrieved documents)
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

const chatApp = workflow.compile({ checkpointer: memory });

export default chatApp;
