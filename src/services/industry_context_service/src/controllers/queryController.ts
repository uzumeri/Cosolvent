import chatService from "@/services/chatService";
import { errorResponse, successResponse } from "@/utils/response";
import type { Context } from "hono";
import { StatusCodes } from "http-status-codes";
import type Redis from "ioredis";
import type { Db } from "mongodb";
import { z } from "zod";

const QueryRequestSchema = z.object({
	question: z.string().min(1),
	threadId: z.string().min(1),
});

const queryPostController = async (c: Context, db: Db, redis: Redis) => {
	const reqBody = await c.req.json();
	const parsedBody = QueryRequestSchema.safeParse(reqBody);

	if (!parsedBody.success) {
		const { status, body } = errorResponse(
			"Invalid request body",
			"BAD_REQUEST",
			StatusCodes.BAD_REQUEST,
		);
		return c.json(body, status);
	}

	const { threadId, question } = reqBody;

	try {
		const response = await chatService(db, redis, { threadId, question });
		const { status, body } = successResponse(response);
		return c.json(body, status);
	} catch (error) {
		const { status, body } = errorResponse(
			"Internal server error",
			"INTERNAL_ERROR",
			StatusCodes.INTERNAL_SERVER_ERROR,
		);
		return c.json(body, status);
	}
};

export default queryPostController;
