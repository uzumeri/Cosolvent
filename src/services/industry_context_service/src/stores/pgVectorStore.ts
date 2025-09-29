import type { EmbeddingsInterface } from "@langchain/core/embeddings";
import { getPgPool } from "@/lib/pg";

export interface PgVectorUpsertRecord {
  id: string;
  embedding: number[];
  metadata?: Record<string, any>;
}

export class PgVectorStore {
  constructor(private embeddings: EmbeddingsInterface, private namespace?: string) {}

  async upsert(records: PgVectorUpsertRecord[]) {
    const pool = getPgPool();
    const client = await pool.connect();
    try {
      await client.query("BEGIN");
      for (const r of records) {
        await client.query(
          `INSERT INTO embeddings (id, embedding, region, certifications, primary_crops)
           VALUES ($1, $2, $3, $4, $5)
           ON CONFLICT (id) DO UPDATE SET embedding = EXCLUDED.embedding, region = EXCLUDED.region, certifications = EXCLUDED.certifications, primary_crops = EXCLUDED.primary_crops`,
          [
            r.id,
            r.embedding,
            r.metadata?.region ?? null,
            r.metadata?.certifications ?? [],
            r.metadata?.primary_crops ?? [],
          ],
        );
      }
      await client.query("COMMIT");
    } catch (e) {
      await client.query("ROLLBACK");
      throw e;
    } finally {
      client.release();
    }
  }

  async similaritySearch(query: string, k: number) {
    const pool = getPgPool();
    const embedding = await this.embeddings.embedQuery(query);
    const { rows } = await pool.query(
      `SELECT id, 1 - (embedding <#> $1::vector) AS score FROM embeddings ORDER BY embedding <#> $1::vector LIMIT $2`,
      [embedding, k],
    );
    return rows.map((r) => ({ id: r.id, score: Number(r.score) }));
  }
}

export const newPgVectorStore = async (
  embeddings: EmbeddingsInterface,
  _indexName: string, // kept for API compatibility
  namespace?: string,
) => new PgVectorStore(embeddings, namespace);
