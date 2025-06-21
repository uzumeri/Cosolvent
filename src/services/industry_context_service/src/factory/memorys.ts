import { MemorySaver } from "@langchain/langgraph";

const newLangGraphMemory = () => {
	return new MemorySaver();
};

export { newLangGraphMemory };
