import queryPostController from "@/controllers/queryController";
import { Hono } from "hono";

const queryRoutes = new Hono();

queryRoutes.post("/", queryPostController);

export default queryRoutes;
