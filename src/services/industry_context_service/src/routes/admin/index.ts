import { Hono } from "hono";
import type Redis from "ioredis";
import type { Db } from "mongodb";
import promptRoutes from "./prompt";

const adminRoutes = (db: Db, redis: Redis) => {
	const router = new Hono();

	router.route("/prompt", promptRoutes(db, redis));

	return router;
};

export default adminRoutes;
