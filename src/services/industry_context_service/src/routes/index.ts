import { Hono } from "hono";
import indexController from "../controllers/indexController.js";

const indexRoutes = new Hono();

indexRoutes.get("/", indexController);

export default indexRoutes;
