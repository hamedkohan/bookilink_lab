# Bookilink Persistent Backend v0.3

This is the backend-capable Bookilink deployment path.

## What persists

- Original PDF / EPUB -> private Supabase Storage bucket `book-files`
- Book metadata -> Supabase Postgres table `books`
- Semantic chunks -> Supabase Postgres table `chunks`
- Embeddings -> pgvector column on `chunks`
- Similarity search -> Postgres RPC `match_book_chunks`

A browser refresh, Streamlit restart, or redeploy does **not** remove the library.

Chat history is still session-only in v0.3.

---

## AI provider

Bookilink uses the Porsit OpenAI-compatible gateway.

Default configuration:

```text
Base URL: https://api-gateway.porsit.cloud/v1
Chat endpoint: /chat/completions
Embeddings endpoint: /embeddings
Chat model: gpt-5.4-mini
Embedding model: text-embedding-3-small
```

The code is in `bookilink/gateway.py`.

Do **not** commit the API key to GitHub.

---

## Streamlit Community Cloud secrets

Open your deployed app in Streamlit Community Cloud and go to:

**App settings -> Secrets**

Paste a TOML configuration like this:

```toml
# Protect the whole lab from public API abuse.
BOOKILINK_APP_PASSWORD = "choose-a-private-password"

# Porsit Gateway
PORSIT_API_KEY = "porsit_sk_live_..."
PORSIT_BASE_URL = "https://api-gateway.porsit.cloud/v1"
PORSIT_CHAT_MODEL = "gpt-5.4-mini"
PORSIT_EMBEDDING_MODEL = "text-embedding-3-small"

# Supabase persistence
SUPABASE_URL = "https://YOUR_PROJECT_REF.supabase.co"
SUPABASE_SECRET_KEY = "sb_secret_..."
SUPABASE_BOOK_BUCKET = "book-files"
```

The legacy `SUPABASE_SERVICE_ROLE_KEY` is also accepted by the code, but a modern `sb_secret_...` backend key is preferred.

### Important

- `PORSIT_API_KEY` stays in Streamlit server secrets.
- `SUPABASE_SECRET_KEY` is elevated and bypasses RLS. Keep it backend-only.
- Never put either secret in `preview.py`, README examples with real values, GitHub issues, screenshots, or frontend JavaScript.
- The persistent app refuses to run without `BOOKILINK_APP_PASSWORD` so a public Streamlit URL cannot silently burn API credits.

---

## Supabase schema

Apply:

```text
supabase/migrations/001_bookilink_persistence.sql
```

It creates:

```text
public.books
public.chunks
match_book_chunks(...)
private storage bucket: book-files
pgvector extension
HNSW vector index
```

The migration enables RLS on the public tables and grants the backend service role access. No public row policies are created.

---

## Deploy the persistent app

In Streamlit Community Cloud create/deploy an app with:

```text
Repository: hamedkohan/bookilink_lab
Branch: main
Main file path: app_persistent.py
```

Then add the Secrets above and reboot the app.

Do not use `preview.py` for the backend version. `preview.py` is intentionally a browser-only demonstration.

---

## Upload flow

```text
PDF / EPUB
   -> local parse in Streamlit server
   -> semantic chunking
   -> Porsit Gateway /v1/embeddings
   -> original file -> private Supabase Storage
   -> metadata/chunks/vectors -> Supabase Postgres
   -> persistent library
```

After that:

```text
question
   -> Porsit embedding
   -> pgvector similarity search
   -> retrieved passages
   -> Porsit /v1/chat/completions
   -> grounded answer + evidence
```

---

## Diagnostics

The persistent app includes a `Diagnostics` tab.

- **Test database connection**: does not spend AI credits.
- **Test gateway**: sends a tiny model request and may consume a very small amount of gateway credit.

---

## Current limitations

1. Image-only / scanned PDFs need OCR and are not supported yet.
2. Chat history is not persisted yet.
3. There is no user/account model yet; the whole private lab is protected by one password.
4. Book deletion / re-index controls should be added before wider use.
5. Free-tier Supabase limits are fine for experimentation, but a large book library with 1536-dimensional embeddings can eventually become database-size heavy.
