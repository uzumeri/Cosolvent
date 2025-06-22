import { Hono } from "hono";
import { auth } from "./lib/auth";

const main = async () => {
	const app = new Hono();

	app.on(["POST", "GET"], "/api/auth/**", (c) => auth.handler(c.req.raw));

	return app;
};

export default await main();
