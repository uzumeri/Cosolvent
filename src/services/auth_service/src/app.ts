import { Hono } from "hono";
import { cors } from "hono/cors";
import { auth } from "./lib/auth";
import verifyRoutes from "./routes/verify";
import env from "./config/env";

const main = async () => {
  const app = new Hono();

  app.use(
    "*",
    cors({
      origin: env.FRONTEND_URL,
      allowMethods: ["POST", "GET", "OPTIONS"],
      credentials: true,
    }),
  );

  app.on(["POST", "GET"], "/api/auth/*", (c) => auth.handler(c.req.raw));

  app.route("/api/verify", verifyRoutes);

  return app;
};

export default await main();
