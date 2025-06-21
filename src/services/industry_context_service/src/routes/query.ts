import queryPostController from "@/controllers/queryController";
import { Hono } from "hono";
import type Redis from "ioredis";
import type { Db } from "mongodb";

const queryRoutes = (db: Db, redis: Redis) => {
	const router = new Hono();

	router.post("/", (c) => queryPostController(c, db, redis));

	return router;
};

export default queryRoutes;
