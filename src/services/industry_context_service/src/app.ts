import { Hono } from "hono";
import indexRoutes from "./routes";
import queryRoutes from "./routes/query";

const app = new Hono();

app.route("/", indexRoutes);
app.route("/query", queryRoutes);

export default app;
