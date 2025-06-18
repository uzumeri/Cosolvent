import { getPrompt, setPrompt } from "@/controllers/promptController";
import { PromptService } from "@/services/promptService";
import { Hono } from "hono";
import type Redis from "ioredis";
import type { Db } from "mongodb";

const promptRoutes = (db: Db, redis: Redis) => {
	const router = new Hono();

	const ps = new PromptService(db, redis);

	router.get("/", getPrompt(ps));
	router.post("/", setPrompt(ps));

	return router;
};

export default promptRoutes;
