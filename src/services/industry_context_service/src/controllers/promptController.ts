import { errorResponse, successResponse } from "@/utils/response";
import type { Context } from "hono";
import { StatusCodes } from "http-status-codes";
import type { PromptService } from "../services/promptService";

const setPrompt = (promptService: PromptService) => async (c: Context) => {
	const { prompt } = await c.req.json();
	if (!prompt)
		return c.json(
			errorResponse(
				"Prompt is required",
				"BAD_REQUEST",
				StatusCodes.BAD_REQUEST,
			),
		);

	try {
		await promptService.setPrompt(prompt);

		return c.json(
			successResponse("Prompt updated successfully", "SUCCESS", StatusCodes.OK),
		);
	} catch (error) {
		return c.json(
			errorResponse(
				"something went wrong, while updating prompt",
				"INTERNAL_ERROR",
				StatusCodes.INTERNAL_SERVER_ERROR,
			),
		);
	}
};

const getPrompt = (promptService: PromptService) => async (c: Context) => {
	try {
		const prompt = await promptService.getPrompt();

		return c.json(successResponse(prompt, "SUCCESS", StatusCodes.OK));
	} catch (error) {
		return c.json(
			errorResponse(
				"something went wrong, while getting prompt",
				"INTERNAL_ERROR",
				StatusCodes.INTERNAL_SERVER_ERROR,
			),
		);
	}
};

export { setPrompt, getPrompt };
