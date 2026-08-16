from __future__ import annotations

import hmac
import os

import streamlit as st
from dotenv import load_dotenv

from bookilink.chunking import chunk_segments
from bookilink.gateway import GatewayLLMProvider
from bookilink.parsers import parse_book
from bookilink.services import answer_book_question, debate_books, generate_book_dna
from bookilink.supabase_rest_store import SupabaseRestBookStore

load_dotenv()

st.set_page_config(page_title="Bookilink Lab · Persistent", page_icon="✦", layout="wide")

st.markdown(
    """
<style>
:root {
  --bg:#090d17; --panel:#111827; --line:rgba(255,255,255,.08);
  --text:#f6f7fb; --muted:#9ca7bd; --accent:#7c5cff; --accent2:#20c7d9;
}
.stApp {
  background:
    radial-gradient(circle at 12% 0%, rgba(124,92,255,.13), transparent 26%),
    radial-gradient(circle at 90% 8%, rgba(32,199,217,.10), transparent 22%),
    #090d17;
}
.block-container {max-width:1200px; padding-top:1.5rem; padding-bottom:3rem;}
.hero {border:1px solid var(--line); border-radius:24px; padding:1.5rem 1.6rem; margin-bottom:1rem;
  background:linear-gradient(135deg,rgba(255,255,255,.045),rgba(255,255,255,.02));}
.kicker {font-size:.74rem; letter-spacing:.14em; text-transform:uppercase; color:#9ca7bd;}
.hero h1 {font-size:clamp(2.1rem,4vw,3.2rem); letter-spacing:-.05em; margin:.4rem 0 .35rem;}
.hero p {color:#aeb8cd; font-size:1rem; max-width:800px; line-height:1.65;}
.status {border:1px solid var(--line); border-radius:14px; padding:.7rem .9rem; background:rgba(255,255,255,.025);}
.book-card {border:1px solid var(--line); border-radius:18px; padding:1rem; min-height:130px; background:rgba(255,255,255,.025);}
.book-title {font-weight:700; font-size:1.02rem; color:#f6f7fb;}
.book-meta {color:#93a0b8; font-size:.86rem; margin-top:.25rem;}
.tag {display:inline-block; margin-top:.7rem; padding:.32rem .55rem; border-radius:999px; font-size:.78rem;
  border:1px solid rgba(124,92,255,.25); background:rgba(124,92,255,.10); color:#d9d4ff;}
.source {border:1px solid var(--line); border-radius:14px; padding:.8rem; margin-bottom:.6rem; background:rgba(255,255,255,.02);}
[data-testid="stSidebar"] {background:#0b101c; border-right:1px solid var(--line);}
div[data-baseweb="tab-list"] {gap:.4rem; padding:.35rem; border:1px solid var(--line); border-radius:14px; background:rgba(255,255,255,.02);}
button[data-baseweb="tab"] {border-radius:10px!important;}
.stButton>button {border-radius:12px; font-weight:600;}
</style>
<div class="hero">
  <div class="kicker">BOOKILINK / PERSISTENT LAB</div>
  <h1>Your library should survive the refresh.</h1>
  <p>PDF/EPUB files are stored in Supabase Storage, semantic chunks and embeddings live in Postgres + pgvector, and AI calls go through the Porsit OpenAI-compatible gateway.</p>
</div>
""",
    unsafe_allow_html=True,
)


def secret(name: str) -> str:
    try:
        value = st.secrets.get(name, "")
        return str(value) if value is not None else ""
    except Exception:
        return os.getenv(name, "")


def require_password() -> None:
    required = secret("BOOKILINK_APP_PASSWORD")
    if not required:
        st.error("امنیت اپ هنوز تنظیم نشده: BOOKILINK_APP_PASSWORD را در Streamlit Secrets بگذار.")
        st.caption("این نسخه عمداً بدون password بالا نمی‌آید تا API key و هزینه مصرف در یک لینک عمومی قابل سوءاستفاده نباشد.")
        st.stop()

    if st.session_state.get("bookilink_authenticated"):
        return

    st.markdown("### Private lab access")
    entered = st.text_input("Password", type="password")
    if st.button("Enter", type="primary"):
        if hmac.compare_digest(entered, required):
            st.session_state["bookilink_authenticated"] = True
            st.rerun()
        else:
            st.error("Password نادرست است.")
    st.stop()


require_password()

supabase_url = secret("SUPABASE_URL")
supabase_secret = secret("SUPABASE_SECRET_KEY") or secret("SUPABASE_SERVICE_ROLE_KEY")
bucket = secret("SUPABASE_BOOK_BUCKET") or "book-files"

gateway_base_url = secret("PORSIT_BASE_URL") or "https://api-gateway.porsit.cloud/v1"
gateway_model = secret("PORSIT_CHAT_MODEL") or "gpt-5.4-mini"
embedding_model = secret("PORSIT_EMBEDDING_MODEL") or "text-embedding-3-small"
gateway_secret = secret("PORSIT_API_KEY")

with st.sidebar:
    st.markdown("### Bookilink backend")
    language = st.segmented_control("Output", ["فارسی", "English"], default="فارسی")
    st.divider()
    st.caption("AI Gateway")
    st.code(gateway_base_url, language=None)
    st.caption(f"Chat: {gateway_model}")
    st.caption(f"Embeddings: {embedding_model}")

    if gateway_secret:
        api_key = gateway_secret
        st.success("Gateway key configured")
    else:
        api_key = st.text_input(
            "Temporary Porsit API key",
            type="password",
            help="برای تست موقت. بعد از refresh پاک می‌شود. برای نسخه پایدار PORSIT_API_KEY را در Streamlit Secrets بگذار.",
        )
        st.warning("Gateway key هنوز در Secrets نیست.")

    st.divider()
    st.caption("Persistence")
    if supabase_url and supabase_secret:
        st.success("Supabase configured")
    else:
        st.error("Supabase secrets missing")

if not supabase_url or not supabase_secret:
    st.error("Persistent backend هنوز کامل کانفیگ نشده است.")
    st.markdown(
        """
در Streamlit Community Cloud → **App settings → Secrets** این دو مقدار را اضافه کن:

```toml
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_SECRET_KEY = "sb_secret_..."
```

بعد app را reboot کن. راهنمای کامل داخل `docs/PERSISTENT_BACKEND.md` است.
"""
    )
    st.stop()

store = SupabaseRestBookStore(supabase_url, supabase_secret, bucket=bucket)


def get_llm() -> GatewayLLMProvider | None:
    if not api_key:
        st.error("Porsit API key لازم است. آن را موقتاً در Sidebar وارد کن یا PORSIT_API_KEY را در Secrets بگذار.")
        return None
    return GatewayLLMProvider(
        api_key,
        base_url=gateway_base_url,
        model=gateway_model,
        embedding_model=embedding_model,
    )


def label(book: dict) -> str:
    return f"{book['title']} — {book.get('author') or 'Unknown author'}"


def sources_box(sources: list[dict], title: str = "Grounding sources") -> None:
    with st.expander(f"{title} · {len(sources)} excerpts"):
        for source in sources:
            score = source.get("score")
            score_text = f" · score {score:.3f}" if isinstance(score, (int, float)) else ""
            st.markdown(
                f"<div class='source'><b>[{source['label']}]</b> · {source['locator']}{score_text}<br><br>{source['text'][:1400]}</div>",
                unsafe_allow_html=True,
            )


library_tab, dna_tab, talk_tab, debate_tab, diagnostics_tab = st.tabs(
    ["📚 Library", "🧬 Book DNA", "💬 Talk", "⚔️ Debate", "⚙️ Diagnostics"]
)

with library_tab:
    c1, c2 = st.columns([1.05, .95], gap="large")
    with c1:
        st.subheader("Upload a book")
        uploaded = st.file_uploader("PDF or EPUB", type=["pdf", "epub"], accept_multiple_files=False)
        if uploaded:
            st.caption(f"{uploaded.name} · {uploaded.size / 1024 / 1024:.1f} MB")

        if st.button("Ingest, embed & save", type="primary", disabled=uploaded is None):
            llm = get_llm()
            if llm and uploaded:
                file_bytes = uploaded.getvalue()
                book_id, file_hash = store.make_book_id(file_bytes)
                if store.has_book(book_id):
                    st.success("این کتاب قبلاً در دیتابیس موجود است و بعد از refresh هم باقی می‌ماند.")
                else:
                    try:
                        with st.status("Building persistent book index…", expanded=True) as status:
                            parsed = parse_book(file_bytes, uploaded.name)
                            st.write(f"Text sections: {len(parsed.segments)}")
                            chunks = chunk_segments(parsed.segments)
                            st.write(f"Semantic chunks: {len(chunks)}")
                            embeddings = llm.embed([chunk.text for chunk in chunks])
                            st.write("Embeddings created through Porsit Gateway")

                            content_type = "application/pdf" if parsed.file_type == "pdf" else "application/epub+zip"
                            storage_path = store.upload_source_file(
                                book_id=book_id,
                                filename=uploaded.name,
                                file_bytes=file_bytes,
                                content_type=content_type,
                            )
                            st.write("Original file saved to private Supabase Storage")

                            store.save_book(
                                book_id=book_id,
                                title=parsed.title,
                                author=parsed.author,
                                filename=uploaded.name,
                                file_type=parsed.file_type,
                                file_hash=file_hash,
                                chunks=chunks,
                                embeddings=embeddings,
                                metadata={"embedding_model": embedding_model, "gateway_model": gateway_model},
                                storage_path=storage_path,
                            )
                            status.update(label="Persisted successfully", state="complete", expanded=False)
                        st.success(f"{parsed.title} ذخیره شد.")
                        st.rerun()
                    except Exception as exc:
                        st.exception(exc)

    with c2:
        st.subheader("Persistence model")
        st.markdown(
            """
- **Original file** → private Supabase Storage  
- **Book metadata** → Postgres  
- **Chunks** → Postgres  
- **Embeddings** → pgvector  
- **Similarity search** → database RPC  
- **Chat history** → فعلاً session-only
"""
        )

    books = store.list_books()
    st.markdown("### Persistent library")
    if not books:
        st.info("هنوز کتابی ذخیره نشده.")
    else:
        cols = st.columns(3)
        for i, book in enumerate(books):
            with cols[i % 3]:
                st.markdown(
                    f"""
<div class="book-card">
  <div class="book-title">{book['title']}</div>
  <div class="book-meta">{book.get('author') or 'Unknown author'}</div>
  <div class="book-meta">{book.get('filename') or ''}</div>
  <span class="tag">{book.get('chunk_count', 0)} chunks · persistent</span>
</div>
""",
                    unsafe_allow_html=True,
                )

with dna_tab:
    books = store.list_books()
    if not books:
        st.info("اول یک کتاب در Library ذخیره کن.")
    else:
        by_id = {book["id"]: book for book in books}
        book_id = st.selectbox("Book", list(by_id), format_func=lambda value: label(by_id[value]), key="persistent_dna")
        if st.button("Generate Book DNA", type="primary"):
            llm = get_llm()
            if llm:
                try:
                    with st.spinner("Mapping the intellectual DNA…"):
                        answer, sources = generate_book_dna(store, llm, book_id, language or "فارسی")
                    st.session_state["persistent_dna_result"] = (book_id, answer, sources)
                except Exception as exc:
                    st.exception(exc)

        result = st.session_state.get("persistent_dna_result")
        if result and result[0] == book_id:
            st.markdown(result[1])
            sources_box(result[2], "DNA evidence")

with talk_tab:
    books = store.list_books()
    if not books:
        st.info("اول یک کتاب در Library ذخیره کن.")
    else:
        by_id = {book["id"]: book for book in books}
        c1, c2 = st.columns(2)
        with c1:
            book_id = st.selectbox("Book", list(by_id), format_func=lambda value: label(by_id[value]), key="persistent_talk")
        with c2:
            mode = st.selectbox("Mode", ["Talk", "Interrogate", "Skeptical", "Devil's advocate", "Academic critique"])

        history_key = f"persistent_chat_{book_id}_{mode}"
        history = st.session_state.setdefault(history_key, [])
        for message in history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message.get("sources"):
                    sources_box(message["sources"], "Sources")

        question = st.chat_input("Ask the book something…")
        if question:
            history.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)
            llm = get_llm()
            if llm:
                try:
                    with st.chat_message("assistant"):
                        with st.spinner("Retrieving passages…"):
                            answer, sources = answer_book_question(
                                store,
                                llm,
                                book_id,
                                question,
                                language or "فارسی",
                                mode,
                                history=history[:-1],
                            )
                        st.markdown(answer)
                        sources_box(sources, "Sources")
                    history.append({"role": "assistant", "content": answer, "sources": sources})
                except Exception as exc:
                    st.exception(exc)

with debate_tab:
    books = store.list_books()
    if len(books) < 2:
        st.info("برای Debate حداقل دو کتاب ذخیره کن.")
    else:
        by_id = {book["id"]: book for book in books}
        ids = list(by_id)
        c1, c2 = st.columns(2)
        with c1:
            a = st.selectbox("Book A", ids, index=0, format_func=lambda value: label(by_id[value]))
        with c2:
            b = st.selectbox("Book B", ids, index=1, format_func=lambda value: label(by_id[value]))
        question = st.text_area("Debate question", placeholder="دو کتاب باید سر چه چیزی با هم اختلاف پیدا کنند؟")
        if st.button("Start Debate", type="primary", disabled=not question.strip() or a == b):
            llm = get_llm()
            if llm:
                try:
                    with st.spinner("Putting both books in the same room…"):
                        answer, sources = debate_books(store, llm, a, b, question, language or "فارسی")
                    st.session_state["persistent_debate"] = (a, b, question, answer, sources)
                except Exception as exc:
                    st.exception(exc)
        result = st.session_state.get("persistent_debate")
        if result and result[:3] == (a, b, question):
            st.markdown(result[3])
            sources_box(result[4], "Debate evidence")

with diagnostics_tab:
    st.subheader("Backend diagnostics")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Supabase")
        st.caption(supabase_url)
        if st.button("Test database connection"):
            try:
                if store.ping():
                    st.success("Database connection OK")
                else:
                    st.error("Unexpected database response")
            except Exception as exc:
                st.exception(exc)
    with c2:
        st.markdown("#### Porsit Gateway")
        st.caption(f"{gateway_base_url} · {gateway_model}")
        if st.button("Test gateway", disabled=not bool(api_key)):
            try:
                llm = get_llm()
                if llm:
                    answer = llm.generate("Reply with exactly OK.", "health check")
                    st.success(f"Gateway replied: {answer[:100]}")
            except Exception as exc:
                st.exception(exc)

st.caption("Bookilink Persistent v0.3 · Supabase Postgres/pgvector + private Storage · Porsit OpenAI-compatible Gateway")
