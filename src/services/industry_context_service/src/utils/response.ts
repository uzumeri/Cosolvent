import type { ContentfulStatusCode } from "hono/utils/http-status";
import { StatusCodes, getReasonPhrase } from "http-status-codes";

export type SuccessCode = "SUCCESS";
export type ErrorCode =
	| "INTERNAL_ERROR"
	| "NOT_FOUND"
	| "BAD_REQUEST"
	| "METHOD_NOT_ALLOWED";

export const successResponse = <T>(
	data: T,
	code: SuccessCode = "SUCCESS",
	status: ContentfulStatusCode = StatusCodes.OK,
) => ({
	status,
	body: {
		success: true,
		code,
		statusCode: status,
		message: getReasonPhrase(status),
		data,
	},
});

export const errorResponse = (
	message: string,
	code: ErrorCode = "INTERNAL_ERROR",
	status: ContentfulStatusCode = StatusCodes.INTERNAL_SERVER_ERROR,
) => ({
	status,
	body: {
		success: false,
		code,
		statusCode: status,
		message,
	},
});
