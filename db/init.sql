-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Producers table (denormalized files JSONB for minimal changes)
CREATE TABLE IF NOT EXISTS producers (
  id TEXT PRIMARY KEY,
  farm_name TEXT NOT NULL,
  contact_name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  phone TEXT NOT NULL,
  address TEXT NOT NULL,
  country TEXT NOT NULL DEFAULT 'Canada',
  region TEXT NOT NULL,
  farm_size DOUBLE PRECISION NOT NULL,
  annual_production DOUBLE PRECISION NOT NULL,
  farm_description TEXT NOT NULL,
  primary_crops TEXT[] NOT NULL DEFAULT '{}',
  certifications TEXT[] NOT NULL DEFAULT '{}',
  export_experience TEXT NOT NULL,
  status TEXT NOT NULL,
  files JSONB NOT NULL DEFAULT '[]'::jsonb,
  ai_profile TEXT,
  ai_profile_draft TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Producer files (asset service)
CREATE TABLE IF NOT EXISTS producer_files (
  id TEXT PRIMARY KEY,
  profile_id TEXT NOT NULL,
  url TEXT NOT NULL,
  file_type TEXT NOT NULL,
  certification TEXT,
  description TEXT,
  priority INT DEFAULT 0,
  privacy TEXT DEFAULT 'private',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_producer_files_profile ON producer_files(profile_id);

-- Templates (profile templates)
CREATE TABLE IF NOT EXISTS templates (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  content TEXT NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_templates_active ON templates(is_active);

-- Embeddings for search (pgvector)
-- IMPORTANT: ivfflat indexes require a fixed dimension on the column.
-- Set this to match your embedding model dimension (e.g., 1536 for many OpenAI embeddings).
-- If you need a different dimension, update the line below and reinitialize the DB volume.
CREATE TABLE IF NOT EXISTS embeddings (
  id TEXT PRIMARY KEY,
  embedding vector(1536),
  region TEXT,
  certifications TEXT[] DEFAULT '{}',
  primary_crops TEXT[] DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_embeddings_vec ON embeddings USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_embeddings_region ON embeddings(region);

-- Singleton app config for LLM orchestration
CREATE TABLE IF NOT EXISTS app_config (
  id TEXT PRIMARY KEY,
  data JSONB NOT NULL
);

-- Documents for industry_context_service (metadata + processing status)
CREATE TABLE IF NOT EXISTS documents (
  doc_id TEXT PRIMARY KEY,
  filename TEXT NOT NULL,
  mime_type TEXT NOT NULL,
  size BIGINT NOT NULL,
  path TEXT NOT NULL,
  status TEXT NOT NULL,
  error TEXT,
  job_id TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_documents_created ON documents(created_at DESC);

-- System prompts table (could be merged into app_config later)
CREATE TABLE IF NOT EXISTS system_prompts (
  id TEXT PRIMARY KEY,
  prompt TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Generic Participants table for any market
CREATE TABLE IF NOT EXISTS participants (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL, -- e.g., 'exporter', 'importer', 'developer'
  email TEXT UNIQUE,
  data JSONB NOT NULL DEFAULT '{}'::jsonb,
  status TEXT NOT NULL DEFAULT 'active',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Generic Participant Embeddings (mapping to participants table)
CREATE TABLE IF NOT EXISTS participant_embeddings (
  id TEXT PRIMARY KEY REFERENCES participants(id) ON DELETE CASCADE,
  embedding vector(1536),
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb, -- Store filterable fields here
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_participant_embeddings_vec ON participant_embeddings USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_participant_embeddings_meta ON participant_embeddings USING gin (metadata);
