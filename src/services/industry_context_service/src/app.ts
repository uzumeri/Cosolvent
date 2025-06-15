import { Hono } from "hono";
import indexRoutes from "./routes";

const app = new Hono();

app.route("/", indexRoutes);

export default app;
