import { getPgPool } from "@/lib/pg";
import type { DocumentSchema } from "@/models/document";

export const insertDocument = async (doc: DocumentSchema) => {
  const pool = getPgPool();
  await pool.query(
    `INSERT INTO documents (doc_id, filename, mime_type, size, path, status, job_id, created_at, updated_at)
     VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
     ON CONFLICT (doc_id) DO NOTHING`,
    [
      doc.docId,
      doc.filename,
      doc.mimeType,
      doc.size,
      doc.path,
      doc.status,
      doc.jobId,
      doc.createdAt,
      doc.updatedAt,
    ],
  );
};

export const updateStatus = async (docId: string, status: string, error?: string) => {
  const pool = getPgPool();
  await pool.query(
    `UPDATE documents SET status = $2, error = $3, updated_at = NOW() WHERE doc_id = $1`,
    [docId, status, error ?? null],
  );
};

export const setJobId = async (docId: string, jobId: string) => {
  const pool = getPgPool();
  await pool.query(`UPDATE documents SET job_id = $2, updated_at = NOW() WHERE doc_id = $1`, [docId, jobId]);
};

export const findByDocId = async (docId: string) => {
  const pool = getPgPool();
  const { rows } = await pool.query(`SELECT * FROM documents WHERE doc_id = $1`, [docId]);
  return rows[0] ?? null;
};

export const deleteByDocId = async (docId: string) => {
  const pool = getPgPool();
  await pool.query(`DELETE FROM documents WHERE doc_id = $1`, [docId]);
};

export const listAll = async (): Promise<any[]> => {
  const pool = getPgPool();
  const { rows } = await pool.query(`SELECT * FROM documents ORDER BY created_at DESC`);
  return rows;
};
