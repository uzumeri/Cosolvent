import { Hono } from "hono";
import type Redis from "ioredis";
import type { Db } from "mongodb";
import promptRoutes from "./prompt";
import documentRoutes from "./document";
import type { PineconeStore } from "@langchain/pinecone";

const adminRoutes = (db: Db, redis: Redis, pinecone: PineconeStore) => {
	const router = new Hono();

	router.route("/document", documentRoutes(db, redis, pinecone));
	router.route("/prompt", promptRoutes(db, redis));

	return router;
};

export default adminRoutes;
