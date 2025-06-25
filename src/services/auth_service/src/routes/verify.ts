import { auth } from "@/lib/auth";
import { errorResponse } from "@/utils/response";
import { Hono, type Context } from "hono";
import { StatusCodes } from "http-status-codes";

const verifyRoutes = new Hono();

// this route is used to verify the session by the api getways/reverse proxy
const verify = async (c: Context) => {
	try {
		const repose = await auth.api.getSession({
			headers: c.req.raw.headers,
		});

		if (repose === null) {
			const { status, body } = errorResponse(
				"Unauthorized",
				"UNAUTHORIZED",
				StatusCodes.UNAUTHORIZED,
			);

			return c.json(body, status);
		}

		return c.json(repose, StatusCodes.OK);
	} catch (error) {
		const { status, body } = errorResponse(
			"Internal server error",
			"INTERNAL_ERROR",
			StatusCodes.INTERNAL_SERVER_ERROR,
		);

		return c.json(body, status);
	}
};

verifyRoutes.get("/", verify);

export default verifyRoutes;
