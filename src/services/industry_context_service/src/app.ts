import { Hono } from "hono";
import { connectToDB } from "./lib/db";
import connectToRedis from "./lib/redis";
import indexRoutes from "./routes";
import adminRoutes from "./routes/admin";
import queryRoutes from "./routes/query";

const main = async () => {
	const app = new Hono();
	const db = await connectToDB();
	const redis = await connectToRedis();

	app.route("/", indexRoutes);
	app.route("/admin", adminRoutes(db, redis));
	app.route("/query", queryRoutes(db, redis));

	return app;
};

export default await main();
