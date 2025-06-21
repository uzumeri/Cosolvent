import env from "@/config/env";
import { type Db, MongoClient } from "mongodb";

let dbInstance: Db | null = null;

export const connectToDB = async (): Promise<Db> => {
	if (dbInstance) return dbInstance;

	const client = new MongoClient(env.MONGODB_URI);
	await client.connect();

	dbInstance = client.db();

	return dbInstance;
};
