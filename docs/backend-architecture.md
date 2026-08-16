# Bookilink backend architecture

## Goal

Persist books and semantic indexes across refreshes and deployments while keeping API secrets server-side.

## Flow

```text
PDF / EPUB upload
  -> parse
  -> semantic chunking
  -> OpenAI embeddings
  -> original file -> Supabase Storage (private bucket)
  -> metadata -> Supabase Postgres books
  -> chunks + embeddings -> Supabase Postgres chunks / pgvector

Book DNA / Talk / Debate
  -> embed query
  -> match_book_chunks RPC
  -> grounded source excerpts
  -> OpenAI Responses API
  -> answer + evidence
```

## Prototype vs production

The persistent backend is appropriate for a private/product-lab deployment. A future public multi-user release should add Supabase Auth, ownership columns, per-user RLS policies, quotas, ingestion jobs, and background processing for large books.
