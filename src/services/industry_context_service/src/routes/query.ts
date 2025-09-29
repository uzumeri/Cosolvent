import queryPostController from "@/controllers/queryController";
import { Hono } from "hono";
import type { Context } from "hono";
import type Redis from "ioredis";

const queryRoutes = (redis: Redis) => {
	const router = new Hono();

	router.post("/", (c: Context) => queryPostController(c, redis));

	return router;
};

export default queryRoutes;
