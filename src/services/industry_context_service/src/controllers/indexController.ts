import type { Context } from "hono";

const indexController = (c: Context) => {
	return c.text("Hello Hono!");
};

export default indexController;
