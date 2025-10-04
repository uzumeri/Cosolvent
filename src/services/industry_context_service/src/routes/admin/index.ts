import { Hono } from "hono";
import type Redis from "ioredis";
import promptRoutes from "./prompt";
import documentRoutes from "./document";
import type { PgVectorStore } from "@/stores/pgVectorStore";

const adminRoutes = (redis: Redis, store: PgVectorStore) => {
	const router = new Hono();

	router.route("/document", documentRoutes(redis, store));
	router.route("/prompt", promptRoutes(redis));

	return router;
};

export default adminRoutes;
