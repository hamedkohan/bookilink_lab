create extension if not exists vector with schema extensions;

create table if not exists public.books (
  id text primary key,
  title text not null,
  author text,
  filename text not null,
  file_type text not null,
  file_hash text not null,
  chunk_count integer not null default 0,
  metadata_json jsonb not null default '{}'::jsonb,
  storage_path text,
  created_at timestamptz not null default now()
);

create table if not exists public.chunks (
  book_id text not null references public.books(id) on delete cascade,
  chunk_index integer not null,
  locator text not null,
  text text not null,
  embedding extensions.vector(1536) not null,
  primary key (book_id, chunk_index)
);

create index if not exists idx_chunks_book on public.chunks(book_id);
create index if not exists idx_chunks_embedding_hnsw on public.chunks using hnsw (embedding vector_cosine_ops);

create or replace function public.match_book_chunks(
  query_embedding extensions.vector(1536),
  target_book_id text,
  match_count integer default 7
)
returns table (
  chunk_index integer,
  locator text,
  text text,
  similarity double precision
)
language sql
stable
as $$
  select
    c.chunk_index,
    c.locator,
    c.text,
    1 - (c.embedding <=> query_embedding) as similarity
  from public.chunks c
  where c.book_id = target_book_id
  order by c.embedding <=> query_embedding
  limit greatest(match_count, 1);
$$;

alter table public.books enable row level security;
alter table public.chunks enable row level security;

grant all on public.books to service_role;
grant all on public.chunks to service_role;
grant execute on function public.match_book_chunks(extensions.vector, text, integer) to service_role;

insert into storage.buckets (id, name, public)
values ('book-files', 'book-files', false)
on conflict (id) do nothing;
