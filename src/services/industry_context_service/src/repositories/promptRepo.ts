import { getPgPool } from "@/lib/pg";

const KEY = "system_prompt";

export const getPrompt = async (): Promise<string | null> => {
  const pool = getPgPool();
  const { rows } = await pool.query<{ prompt: string }>(
    `SELECT prompt FROM system_prompts WHERE id = $1`,
    [KEY]
  );
  return rows[0]?.prompt ?? null;
};

export const setPrompt = async (prompt: string): Promise<void> => {
  const pool = getPgPool();
  await pool.query(
    `INSERT INTO system_prompts (id, prompt, created_at, updated_at)
     VALUES ($1, $2, NOW(), NOW())
     ON CONFLICT (id) DO UPDATE SET prompt = EXCLUDED.prompt, updated_at = NOW()`,
    [KEY, prompt]
  );
};
