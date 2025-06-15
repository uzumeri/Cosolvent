import indexController from "@/controllers/indexController";
import { Hono } from "hono";

const indexRoutes = new Hono();

indexRoutes.get("/", indexController);

export default indexRoutes;
