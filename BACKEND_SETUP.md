# Bookilink persistent backend setup

This version is designed to keep uploaded books across browser refreshes, Streamlit restarts, and redeployments by storing data in Supabase instead of relying only on the local Streamlit filesystem.

## Architecture

- Streamlit: UI and orchestration
- Supabase Postgres: books, chunks, metadata, embeddings
- pgvector: semantic search
- Supabase Storage: original PDF / EPUB files
- OpenAI API: embeddings + reasoning / generation

## Required secrets

Add these to Streamlit Community Cloud → App → Settings → Secrets. Do **not** commit them to GitHub.

```toml
OPENAI_API_KEY = "sk-..."
SUPABASE_URL = "https://YOUR_PROJECT_REF.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "YOUR_SERVER_SIDE_SECRET_KEY"
SUPABASE_BUCKET = "book-files"
```

`SUPABASE_SERVICE_ROLE_KEY` must remain server-side. Never expose it in browser JavaScript or a public repository.

## OpenAI key

Create an OpenAI API key in the OpenAI developer dashboard, then add it as `OPENAI_API_KEY` in Streamlit Secrets. The app should read it from `st.secrets` / environment variables rather than hard-coding it.

For Bookilink, the API is used for:

1. generating embeddings for semantic retrieval;
2. Book DNA synthesis;
3. Talk / Interrogate responses;
4. Book Debate synthesis.

## Supabase database

Apply `supabase/migrations/001_bookilink_persistence.sql` to the dedicated Bookilink Supabase project. It creates:

- `books`
- `chunks`
- `vector` extension
- HNSW vector index
- `match_book_chunks(...)` RPC function
- private `book-files` Storage bucket

The current migration assumes `text-embedding-3-small` embeddings with 1536 dimensions.

## Persistence behavior

After ingesting a book:

1. the original PDF/EPUB is uploaded to Supabase Storage;
2. metadata is saved to `books`;
3. semantic chunks and embeddings are saved to `chunks`;
4. later sessions rebuild the Library view from Supabase;
5. semantic retrieval is performed in Postgres via pgvector.

Therefore a page refresh does not remove the book.

## Local fallback

If Supabase secrets are not configured, Bookilink may use the local SQLite store for development. Local SQLite is convenient for testing but should not be treated as durable persistence on Streamlit Community Cloud.

## Security

For the first private prototype, the backend uses a server-side Supabase secret/service-role key and keeps RLS enabled. This intentionally avoids exposing writable database access to anonymous browser clients.

Before turning Bookilink into a multi-user public product, add Supabase Auth and user-owned library policies so each user can access only their own books.
