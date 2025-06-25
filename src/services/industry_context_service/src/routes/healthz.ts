import { Hono } from "hono";
import { StatusCodes } from "http-status-codes";

const healthzRoutes = new Hono();

healthzRoutes.get("/", (c) => {
	c.status(StatusCodes.OK);
	return c.json({ status: "ok" });
});

export default healthzRoutes;
