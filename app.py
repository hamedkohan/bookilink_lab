from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

from bookilink.chunking import chunk_segments
from bookilink.demo import DEMO_BOOKS, demo_debate, demo_talk
from bookilink.llm import LLMProvider
from bookilink.parsers import parse_book
from bookilink.services import answer_book_question, debate_books, generate_book_dna
from bookilink.store import BookStore

load_dotenv()

st.set_page_config(page_title="Bookilink Lab", page_icon="◒", layout="wide")

st.markdown(
    """
<style>
.block-container {max-width: 1180px; padding-top: 1.5rem; padding-bottom: 4rem;}
.hero {padding: 1.25rem 0 .8rem 0;}
.hero h1 {font-size: clamp(2.2rem, 5vw, 3.4rem); margin-bottom: .15rem; letter-spacing: -0.045em;}
.hero p {font-size: 1.05rem; opacity: .72; margin-top: 0;}
.kicker {font-size: .76rem; letter-spacing: .14em; text-transform: uppercase; opacity: .52;}
.book-chip {padding: .72rem .85rem; border: 1px solid rgba(128,128,128,.25); border-radius: .85rem; margin-bottom: .55rem;}
.mode-note {padding: .75rem 1rem; border: 1px solid rgba(128,128,128,.22); border-radius: .8rem; margin: .25rem 0 1rem 0;}
.source-text {font-size: .88rem; opacity: .78;}
[data-testid="stMetricValue"] {font-size: 1.45rem;}
</style>
<div class="hero">
  <div class="kicker">BOOKILINK / PRODUCT LAB</div>
  <h1>Don't just read the book. Enter it.</h1>
  <p>Book DNA · Talk / Interrogate · Book Debate — grounded in the actual text.</p>
</div>
""",
    unsafe_allow_html=True,
)


def _secret(name: str) -> str:
    try:
        return str(st.secrets.get(name, ""))
    except Exception:
        return os.getenv(name, "")


DB_PATH = os.getenv("BOOKILINK_DB_PATH", "data/bookilink.db")
store = BookStore(DB_PATH)

with st.sidebar:
    st.subheader("Bookilink Lab")
    app_mode = st.radio("Mode", ["Demo", "Live"], horizontal=True, help="Demo works without an API key. Live analyzes your own PDF/EPUB.")

    env_key = _secret("OPENAI_API_KEY")
    api_key = ""
    if app_mode == "Live":
        api_key = st.text_input(
            "OpenAI API key",
            value=env_key,
            type="password",
            help="For Streamlit Cloud, add OPENAI_API_KEY in App secrets. You can also paste a key temporarily here.",
        )
        model = st.selectbox(
            "Reasoning model",
            ["gpt-5.6-terra", "gpt-5.6-luna"],
            index=0,
            help="Terra balances intelligence and cost; Luna is optimized for cost-sensitive workloads.",
        )
    else:
        model = "gpt-5.6-terra"
        st.caption("Demo mode uses prebuilt sample content and makes no API calls.")

    language = st.segmented_control("Output", ["فارسی", "English"], default="فارسی")
    st.divider()
    st.caption("Live embeddings: text-embedding-3-small")
    st.caption("v0.2 · product behavior prototype")

mode_label = "DEMO — no API calls" if app_mode == "Demo" else "LIVE — your own books"
st.markdown(f"<div class='mode-note'><b>{mode_label}</b> · {'برای دیدن سریع تجربه، سه کتاب نمونه آماده‌اند.' if app_mode == 'Demo' else 'PDF/EPUB را وارد کن؛ تحلیل‌ها روی متن بازیابی‌شده grounded می‌شوند.'}</div>", unsafe_allow_html=True)


def get_llm():
    if not api_key:
        st.error("برای Live mode یک OpenAI API key لازم است. آن را در Sidebar وارد کن یا در Streamlit App secrets بگذار.")
        return None
    return LLMProvider(api_key=api_key, model=model)


def book_label(book: dict) -> str:
    author = f" — {book['author']}" if book.get("author") else ""
    return f"{book['title']}{author}"


def show_sources(sources: list[dict], title: str = "Grounding sources"):
    with st.expander(f"{title} · {len(sources)} excerpts"):
        for src in sources:
            st.markdown(f"**[{src['label']}] · {src['locator']}**")
            if "score" in src:
                st.caption(f"retrieval score: {src['score']:.3f}")
            st.markdown(src["text"][:1400])
            st.divider()


library_tab, dna_tab, talk_tab, debate_tab = st.tabs(["Library", "Book DNA", "Talk / Interrogate", "Book Debate"])

with library_tab:
    if app_mode == "Demo":
        st.subheader("Demo library")
        st.caption("این‌ها فقط برای تجربه کردن flow هستند؛ متن کامل کتاب‌ها در اپ ذخیره نشده است.")
        cols = st.columns(3)
        for col, (key, book) in zip(cols, DEMO_BOOKS.items()):
            with col:
                with st.container(border=True):
                    st.markdown(f"### {book['title']}")
                    st.caption(book['author'])
                    st.metric("Semantic chunks", book["chunk_count"])
        st.info("برای آپلود کتاب خودت، از Sidebar روی Live بزن.")
    else:
        c1, c2 = st.columns([1.05, .95], gap="large")
        with c1:
            st.subheader("Add a book")
            uploaded = st.file_uploader("PDF or EPUB", type=["pdf", "epub"], accept_multiple_files=False)
            if uploaded:
                st.caption(f"{uploaded.name} · {uploaded.size / 1024 / 1024:.1f} MB")
            if st.button("Ingest & index", type="primary", disabled=uploaded is None):
                llm = get_llm()
                if llm and uploaded:
                    file_bytes = uploaded.getvalue()
                    book_id, file_hash = store.make_book_id(file_bytes)
                    if store.has_book(book_id):
                        st.success("این کتاب قبلاً ایندکس شده و آماده استفاده است.")
                    else:
                        try:
                            with st.status("Reading the book…", expanded=True) as status:
                                parsed = parse_book(file_bytes, uploaded.name)
                                st.write(f"Extracted {len(parsed.segments)} source sections")
                                chunks = chunk_segments(parsed.segments)
                                st.write(f"Built {len(chunks)} semantic chunks")
                                embeddings = llm.embed([c.text for c in chunks])
                                st.write("Created embeddings")
                                store.save_book(
                                    book_id=book_id,
                                    title=parsed.title,
                                    author=parsed.author,
                                    filename=uploaded.name,
                                    file_type=parsed.file_type,
                                    file_hash=file_hash,
                                    chunks=chunks,
                                    embeddings=embeddings,
                                )
                                status.update(label="Book is ready", state="complete", expanded=False)
                            st.success(f"{parsed.title} وارد Bookilink Lab شد.")
                            st.rerun()
                        except Exception as e:
                            st.exception(e)

        with c2:
            st.subheader("Library")
            books = store.list_books()
            if not books:
                st.info("هنوز کتابی وارد نشده. اگر فقط می‌خواهی محصول را ببینی، Demo mode را روشن کن.")
            for book in books:
                st.markdown(
                    f"<div class='book-chip'><b>{book['title']}</b><br><span style='opacity:.65'>{book.get('author') or 'Unknown author'} · {book['chunk_count']} chunks</span></div>",
                    unsafe_allow_html=True,
                )

with dna_tab:
    if app_mode == "Demo":
        demo_ids = list(DEMO_BOOKS.keys())
        selected_id = st.selectbox("Book", demo_ids, format_func=lambda x: book_label(DEMO_BOOKS[x]), key="demo_dna_book")
        st.caption("Book DNA فقط summary نیست؛ thesis، assumptions، strongest/weakest arguments و takeaways را بیرون می‌کشد.")
        if st.button("Generate Book DNA", type="primary", key="demo_dna_btn"):
            st.session_state["demo_dna_result"] = selected_id
        if st.session_state.get("demo_dna_result") == selected_id:
            book = DEMO_BOOKS[selected_id]
            st.markdown(book["dna"])
            demo_sources = [
                {"label": label, "locator": locator, "score": 0.91 - i * 0.04, "text": text}
                for i, (label, locator, text) in enumerate(book["sources"])
            ]
            show_sources(demo_sources, "Demo evidence")
    else:
        books = store.list_books()
        if not books:
            st.info("اول از تب Library حداقل یک کتاب وارد کن.")
        else:
            id_to_book = {b["id"]: b for b in books}
            selected_id = st.selectbox("Book", list(id_to_book.keys()), format_func=lambda x: book_label(id_to_book[x]), key="dna_book")
            st.caption("DNA از چند retrieval probe ساخته می‌شود تا فقط خلاصه فصل اول یا چند chunk تصادفی نباشد.")
            if st.button("Generate Book DNA", type="primary", key="live_dna_btn"):
                llm = get_llm()
                if llm:
                    try:
                        with st.spinner("Mapping the intellectual DNA…"):
                            dna, sources = generate_book_dna(store, llm, selected_id, language or "فارسی")
                        st.session_state["dna_result"] = (selected_id, dna, sources)
                    except Exception as e:
                        st.exception(e)
            if "dna_result" in st.session_state and st.session_state["dna_result"][0] == selected_id:
                _, dna, sources = st.session_state["dna_result"]
                st.markdown(dna)
                show_sources(sources, "DNA evidence")

with talk_tab:
    if app_mode == "Demo":
        demo_ids = list(DEMO_BOOKS.keys())
        top1, top2 = st.columns(2)
        with top1:
            talk_book_id = st.selectbox("Book", demo_ids, format_func=lambda x: book_label(DEMO_BOOKS[x]), key="demo_talk_book")
        with top2:
            mode = st.selectbox("Mode", ["Talk", "Interrogate", "Skeptical", "Devil's advocate", "Academic critique"], key="demo_talk_mode")

        st.markdown("**Try one:**")
        qcols = st.columns(3)
        suggestions = [
            "آسیب‌پذیرترین ادعای کتاب چیست؟",
            "نویسنده چه چیزی را بیش از حد ساده کرده؟",
            "اگر بخواهم فقط یک ایده را اجرا کنم کدام است؟",
        ]
        for col, q in zip(qcols, suggestions):
            if col.button(q, use_container_width=True):
                st.session_state["demo_question"] = q

        question = st.chat_input("Ask the book something…", key="demo_chat_input")
        if question:
            st.session_state["demo_question"] = question
        active_q = st.session_state.get("demo_question")
        if active_q:
            with st.chat_message("user"):
                st.markdown(active_q)
            answer, sources = demo_talk(talk_book_id, mode, active_q)
            with st.chat_message("assistant"):
                st.markdown(answer)
                show_sources(sources, "Demo sources")
    else:
        books = store.list_books()
        if not books:
            st.info("اول یک کتاب وارد Library کن.")
        else:
            id_to_book = {b["id"]: b for b in books}
            top1, top2 = st.columns([1, 1])
            with top1:
                talk_book_id = st.selectbox("Book", list(id_to_book.keys()), format_func=lambda x: book_label(id_to_book[x]), key="talk_book")
            with top2:
                mode = st.selectbox("Mode", ["Talk", "Interrogate", "Skeptical", "Devil's advocate", "Academic critique"], key="live_talk_mode")

            history_key = f"chat_{talk_book_id}_{mode}"
            if history_key not in st.session_state:
                st.session_state[history_key] = []
            history = st.session_state[history_key]

            for msg in history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    if msg.get("sources"):
                        show_sources(msg["sources"], "Sources")

            question = st.chat_input("Ask the book something…", key="live_chat_input")
            if question:
                history.append({"role": "user", "content": question})
                with st.chat_message("user"):
                    st.markdown(question)
                llm = get_llm()
                if llm:
                    try:
                        with st.chat_message("assistant"):
                            with st.spinner("Reading relevant passages…"):
                                answer, sources = answer_book_question(store, llm, talk_book_id, question, language or "فارسی", mode, history=history[:-1])
                            st.markdown(answer)
                            show_sources(sources, "Sources")
                        history.append({"role": "assistant", "content": answer, "sources": sources})
                    except Exception as e:
                        st.exception(e)

with debate_tab:
    if app_mode == "Demo":
        ids = list(DEMO_BOOKS.keys())
        ca, cb = st.columns(2)
        with ca:
            book_a_id = st.selectbox("Book A", ids, index=0, format_func=lambda x: book_label(DEMO_BOOKS[x]), key="demo_book_a")
        with cb:
            book_b_id = st.selectbox("Book B", ids, index=1, format_func=lambda x: book_label(DEMO_BOOKS[x]), key="demo_book_b")
        question = st.text_area("What should they debate?", value="برای عملکرد بهتر، عادت‌های کوچک مهم‌ترند یا ساختن دوره‌های تمرکز عمیق؟", height=100, key="demo_debate_q")
        if st.button("Start Debate", type="primary", disabled=book_a_id == book_b_id, key="demo_debate_btn"):
            st.session_state["demo_debate_result"] = (book_a_id, book_b_id, question)
        result = st.session_state.get("demo_debate_result")
        if result and result[0] == book_a_id and result[1] == book_b_id:
            answer, sources = demo_debate(book_a_id, book_b_id, question)
            st.markdown(answer)
            show_sources(sources, "Demo debate evidence")
    else:
        books = store.list_books()
        if len(books) < 2:
            st.info("برای Debate حداقل دو کتاب باید در Library داشته باشی.")
        else:
            id_to_book = {b["id"]: b for b in books}
            ids = list(id_to_book.keys())
            ca, cb = st.columns(2)
            with ca:
                book_a_id = st.selectbox("Book A", ids, index=0, format_func=lambda x: book_label(id_to_book[x]), key="live_book_a")
            with cb:
                book_b_id = st.selectbox("Book B", ids, index=1, format_func=lambda x: book_label(id_to_book[x]), key="live_book_b")
            question = st.text_area("What should they debate?", placeholder="مثلاً: آیا تغییر رفتار بیشتر از سیستم‌ها می‌آید یا از تصمیم و اراده فرد؟", height=100, key="live_debate_q")
            if st.button("Start Debate", type="primary", disabled=not question.strip() or book_a_id == book_b_id, key="live_debate_btn"):
                llm = get_llm()
                if llm:
                    try:
                        with st.spinner("Putting the books in the same room…"):
                            answer, sources = debate_books(store, llm, book_a_id, book_b_id, question, language or "فارسی")
                        st.session_state["debate_result"] = (book_a_id, book_b_id, question, answer, sources)
                    except Exception as e:
                        st.exception(e)
            result = st.session_state.get("debate_result")
            if result and result[0] == book_a_id and result[1] == book_b_id:
                st.markdown(result[3])
                show_sources(result[4], "Debate evidence")

st.divider()
st.caption("Bookilink Lab v0.2 · Demo mode + live grounded analysis · SQLite prototype · No OCR yet · Cloud storage is ephemeral in this experiment.")
