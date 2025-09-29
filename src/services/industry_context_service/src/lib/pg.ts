import env from "@/config/env";
import { Pool } from "pg";

let pool: Pool | null = null;

export const getPgPool = (): Pool => {
  if (!pool) {
    pool = new Pool({ connectionString: env.DATABASE_URL });
  }
  return pool;
};

export type PgPool = Pool;
