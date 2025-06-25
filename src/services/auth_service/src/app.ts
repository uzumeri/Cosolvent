import { Hono } from "hono";
import { auth } from "./lib/auth";
import verifyRoutes from "./routes/verify";

const main = async () => {
	const app = new Hono();

	app.on(["POST", "GET"], "/api/auth/**", (c) => auth.handler(c.req.raw));

	app.route("/api/verify", verifyRoutes);

	return app;
};

export default await main();
