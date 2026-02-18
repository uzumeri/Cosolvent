import { auth } from "./src/lib/auth";
import { getMigrations } from "better-auth/db";

async function run() {
    const migrations = await getMigrations(auth);
    console.log(migrations.sql);
}

run().catch(console.error);
