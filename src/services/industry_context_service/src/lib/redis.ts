import env from "@/config/env";
import Redis from "ioredis";

let redisInstance: Redis | null = null;

const connectToRedis = async () => {
	if (redisInstance) return redisInstance;

	redisInstance = new Redis(env.REDIS_URL);

	return redisInstance;
};

export default connectToRedis;
