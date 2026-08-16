import streamlit as st

st.set_page_config(page_title="Bookilink Lab Preview", page_icon="✦", layout="wide")

st.markdown(
    """
<style>
:root {
  --paper:#f4f1e9;
  --paper-2:#ebe6dc;
  --ink:#181713;
  --muted:#6e6a61;
  --line:rgba(24,23,19,.12);
  --accent:#5753d9;
  --accent-soft:#ebeafd;
  --green:#1d7c60;
}

.stApp {
  background:
    radial-gradient(circle at 88% 0%, rgba(87,83,217,.10), transparent 25%),
    linear-gradient(180deg, #f7f4ee 0%, var(--paper) 100%);
  color:var(--ink);
}
.block-container {max-width:1180px; padding-top:1.6rem; padding-bottom:4rem;}
[data-testid="stSidebar"] {background:#171714; border-right:0;}
[data-testid="stSidebar"] * {color:#f4f1e9 !important;}

.hero {
  border-top:1px solid var(--ink);
  border-bottom:1px solid var(--line);
  padding:1.2rem 0 1.7rem;
  margin-bottom:1.1rem;
}
.hero-grid {display:grid; grid-template-columns:1.6fr .85fr; gap:2rem; align-items:end;}
.eyebrow {font-size:.72rem; letter-spacing:.15em; text-transform:uppercase; color:var(--muted); margin-bottom:.85rem;}
.hero h1 {font-family:Georgia, 'Times New Roman', serif; font-size:4.25rem; line-height:.94; letter-spacing:-.055em; font-weight:500; color:var(--ink); margin:0; max-width:850px;}
.hero p {font-size:1.02rem; line-height:1.65; color:var(--muted); margin:1rem 0 0; max-width:760px;}
.hero-note {border-left:1px solid var(--ink); padding-left:1.2rem; color:var(--muted); font-size:.9rem; line-height:1.65;}
.hero-note b {color:var(--ink); font-weight:600;}

.top-strip {display:flex; flex-wrap:wrap; gap:.55rem; margin:.25rem 0 1.2rem;}
.tag {display:inline-flex; align-items:center; padding:.42rem .68rem; border-radius:999px; border:1px solid var(--line); background:rgba(255,255,255,.42); font-size:.78rem; color:#4f4b43;}
.tag.active {background:var(--ink); color:#fff; border-color:var(--ink);}

.demo-note {border:1px solid var(--line); border-radius:16px; background:rgba(255,255,255,.42); padding:.8rem 1rem; color:var(--muted); margin-bottom:1rem;}
.demo-note b {color:var(--ink);}

.editorial-card {border:1px solid var(--line); border-radius:18px; background:rgba(255,255,255,.45); padding:1rem 1.05rem; min-height:150px;}
.editorial-card .num {font-family:Georgia, serif; font-size:2rem; color:var(--ink); margin-bottom:.5rem;}
.editorial-card h4 {font-size:1rem; margin:0 0 .35rem; color:var(--ink);}
.editorial-card p {font-size:.88rem; line-height:1.55; margin:0; color:var(--muted);}

.book-card {border-top:1px solid var(--ink); border-bottom:1px solid var(--line); padding:1.05rem 0 1rem; min-height:145px;}
.book-kicker {font-size:.7rem; letter-spacing:.12em; text-transform:uppercase; color:var(--muted); margin-bottom:.55rem;}
.book-title {font-family:Georgia, serif; font-size:1.45rem; line-height:1.05; color:var(--ink); margin-bottom:.45rem;}
.book-meta {font-size:.86rem; color:var(--muted);}
.book-ready {display:inline-block; margin-top:.8rem; font-size:.75rem; color:var(--green); border:1px solid rgba(29,124,96,.25); background:rgba(29,124,96,.06); padding:.34rem .55rem; border-radius:999px;}

.section-kicker {font-size:.7rem; text-transform:uppercase; letter-spacing:.14em; color:var(--muted); margin-bottom:.3rem;}
.section-title {font-family:Georgia, serif; font-size:2rem; line-height:1.1; color:var(--ink); margin:0 0 .35rem;}
.section-desc {color:var(--muted); font-size:.93rem; line-height:1.55; margin-bottom:1rem;}

.insight-box {border:1px solid var(--line); border-radius:18px; background:#fffdf8; padding:1rem 1.05rem; margin:.55rem 0;}
.insight-label {font-size:.7rem; letter-spacing:.12em; text-transform:uppercase; color:var(--muted); margin-bottom:.45rem;}
.insight-value {font-family:Georgia, serif; font-size:1.18rem; line-height:1.42; color:var(--ink);}

.source {border-left:2px solid var(--accent); padding:.75rem .85rem; background:var(--accent-soft); border-radius:0 12px 12px 0; margin:.6rem 0;}
.source b {color:#35318e;}
.source small {color:#6a66a2;}

.mode-pill {display:inline-block; border:1px solid var(--line); border-radius:999px; padding:.35rem .55rem; font-size:.75rem; color:var(--muted); margin-right:.35rem;}
.mode-pill.active {background:var(--accent); color:#fff; border-color:var(--accent);}

.debate-side {border-top:2px solid var(--ink); background:rgba(255,255,255,.34); padding:1rem; min-height:200px;}
.debate-side h4 {font-family:Georgia, serif; font-size:1.4rem; margin:0 0 .7rem; color:var(--ink);}
.synthesis {border:1px solid var(--ink); border-radius:16px; padding:1rem 1.1rem; background:var(--ink); color:#f7f4ee; margin-top:1rem;}
.synthesis b {color:#fff;}

.footer {margin-top:2rem; padding-top:1rem; border-top:1px solid var(--line); color:var(--muted); font-size:.8rem;}

/* Streamlit controls */
div[data-baseweb="tab-list"] {gap:.3rem; border-bottom:1px solid var(--line); margin-bottom:1rem;}
button[data-baseweb="tab"] {color:#827d73 !important; padding:.72rem .8rem !important; border-radius:10px 10px 0 0 !important;}
button[aria-selected="true"][data-baseweb="tab"] {color:var(--ink) !important; background:transparent !important; border-bottom:2px solid var(--ink) !important;}
.stButton>button {border-radius:999px; border:1px solid var(--ink); background:var(--ink); color:#fff; font-weight:500; padding:.52rem .92rem;}
.stButton>button:hover {background:var(--accent); border-color:var(--accent); color:#fff;}
[data-testid="stChatMessage"] {border:1px solid var(--line); border-radius:16px; background:rgba(255,255,255,.36); padding:.25rem;}
[data-testid="stExpander"] {border:1px solid var(--line); background:rgba(255,255,255,.28); border-radius:14px;}

@media (max-width:900px){
  .hero-grid{grid-template-columns:1fr;}
  .hero h1{font-size:3rem;}
  .hero-note{border-left:0; border-top:1px solid var(--line); padding:1rem 0 0;}
}
</style>

<div class="hero">
  <div class="hero-grid">
    <div>
      <div class="eyebrow">Bookilink / Intelligent reading interface</div>
      <h1>Read less.<br>Think deeper.</h1>
      <p>Bookilink turns a book from a static file into a thinking partner — map its intellectual DNA, pressure-test its arguments, and place multiple books in the same conversation.</p>
    </div>
    <div class="hero-note">
      <b>Not another “chat with PDF.”</b><br>
      The product is designed around interpretation, critique, comparison, and evidence — not generic summaries.
    </div>
  </div>
</div>
<div class="top-strip">
  <span class="tag active">Book DNA</span>
  <span class="tag">Interrogate</span>
  <span class="tag">Debate</span>
  <span class="tag">Evidence-linked</span>
  <span class="tag">PDF · EPUB</span>
</div>
<div class="demo-note"><b>Interactive demo.</b> این نسخه بدون API و backend اجرا می‌شود؛ هدفش تست تجربه و جهت طراحی محصول است.</div>
""",
    unsafe_allow_html=True,
)

BOOKS = {
    "Atomic Habits": {
        "author": "James Clear",
        "theme": "Behavior / Systems",
        "thesis": "تغییر پایدار بیشتر از تصمیم‌های بزرگ، حاصل طراحی سیستم‌های کوچک و تکرارشونده است.",
        "assumption": "فرد حداقل بخشی از محیط و روتینش را می‌تواند بازطراحی کند.",
        "strength": "اتصال رفتار به identity، عادت را از یک task به evidence برای نوعی هویت تبدیل می‌کند.",
        "weakness": "نقش محدودیت‌های ساختاری و تفاوت‌های فردی گاهی کمتر از حد لازم دیده می‌شود.",
        "sources": [("S1", "Chapter 1", "تغییرهای کوچک به‌عنوان ورودی‌های یک سیستم مرکب توضیح داده می‌شوند."), ("S2", "Chapter 2", "identity-based habits رفتار تکراری را به تصور فرد از خودش پیوند می‌دهد."), ("S3", "Chapter 6", "محیط بخشی از معماری انتخاب و کاهش اصطکاک معرفی می‌شود.")],
    },
    "Deep Work": {
        "author": "Cal Newport",
        "theme": "Attention / Performance",
        "thesis": "تمرکز بدون حواس‌پرتی روی کار شناختی سخت، یک skill کمیاب و قابل تمرین است.",
        "assumption": "فرد می‌تواند دست‌کم بخشی از تقویم و انتظارات ارتباطی محیط کارش را کنترل کند.",
        "strength": "Deep work را از preference شخصی به capability اقتصادی تبدیل می‌کند.",
        "weakness": "نسخه کتاب برای نقش‌هایی که پاسخ‌گویی لحظه‌ای جزء خودِ کار است محدودتر می‌شود.",
        "sources": [("S1", "Introduction", "Deep work فعالیت حرفه‌ای بدون حواس‌پرتی است که ظرفیت شناختی را تا مرز توان می‌برد."), ("S2", "Part I", "کتاب میان busyness و تولید ارزش تمایز می‌گذارد."), ("S3", "Rule 2", "تحمل boredom بخشی از بازسازی attention است.")],
    },
    "The Psychology of Money": {
        "author": "Morgan Housel",
        "theme": "Money / Behavior",
        "thesis": "رفتار مالی خوب بیشتر از دانستن فرمول‌ها، به روان‌شناسی و رابطه ما با risk و uncertainty وابسته است.",
        "assumption": "ساختن margin of safety و کنترل رفتار شخصی می‌تواند بخشی از عدم‌قطعیت را قابل تحمل کند.",
        "strength": "نقش luck و risk را وارد داستان‌های موفقیت می‌کند و جلوی روایت‌های بیش از حد ساده را می‌گیرد.",
        "weakness": "بعضی توصیه‌ها آن‌قدر انعطاف‌پذیرند که سخت falsifiable می‌شوند.",
        "sources": [("S1", "Chapter 1", "تجربه شخصی چارچوب متفاوتی برای برداشت از ریسک و پول می‌سازد."), ("S2", "Chapters 2–3", "luck و risk در ارزیابی موفقیت و شکست برجسته می‌شوند."), ("S3", "Chapter 13", "room for error راهی برای بقا در برابر uncertainty است.")],
    },
}


def sources_box(book, prefix="S"):
    with st.expander("Evidence used"):
        for i, (_, locator, text) in enumerate(book["sources"], 1):
            st.markdown(f"<div class='source'><b>[{prefix}{i}]</b> · <small>{locator}</small><br>{text}</div>", unsafe_allow_html=True)


def talk_answer(name, mode, question):
    if name == "Atomic Habits":
        core = "آسیب‌پذیرترین بخش استدلال جایی است که قدرت سیستم شخصی ممکن است بیش از حد از محدودیت‌های واقعی محیط جدا شود. سؤال جدی این است: اگر فرد اختیار بازطراحی محیطش را نداشته باشد، چه مقدار از نسخه کتاب هنوز کار می‌کند؟ [S2][S3]"
    elif name == "Deep Work":
        core = "کتاب attention را درست به‌عنوان capability می‌بیند، اما برای شغل‌هایی که پاسخ‌گویی لحظه‌ای جزء خود کار است نسخه محدودتری دارد. باید پرسید کدام خروجی واقعاً از isolation طولانی سود می‌برد. [S1][S3]"
    else:
        core = "قدرت کتاب در دیدن uncertainty است؛ ضعف احتمالی این است که بعضی توصیه‌ها آن‌قدر انعطاف‌پذیرند که سخت falsifiable می‌شوند. [S2][S3]"
    lead = {"Talk":"از منطق خود کتاب:", "Interrogate":"اگر نویسنده را تحت فشار بگذاریم:", "Skeptical":"از زاویه شکاکانه:", "Devil's advocate":"اگر خلاف کتاب را قوی کنیم:", "Academic critique":"در یک نقد آکادمیک:"}[mode]
    return f"{lead} {core}\n\n**سؤال تو:** {question}"


library, dna, talk, debate = st.tabs(["Library", "Book DNA", "Talk / Interrogate", "Book Debate"])

with library:
    st.markdown("<div class='section-kicker'>Library</div><div class='section-title'>A shelf built for thinking</div><div class='section-desc'>هر کتاب یک source برای چند تجربه مختلف است؛ نه یک فایل جدا برای یک chatbot جدا.</div>", unsafe_allow_html=True)
    cols = st.columns(3)
    for col, (title, book) in zip(cols, BOOKS.items()):
        with col:
            st.markdown(f"""
            <div class='book-card'>
              <div class='book-kicker'>{book['theme']}</div>
              <div class='book-title'>{title}</div>
              <div class='book-meta'>{book['author']}</div>
              <span class='book-ready'>Ready for analysis</span>
            </div>""", unsafe_allow_html=True)
    st.markdown("### Three product behaviors")
    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown("<div class='editorial-card'><div class='num'>01</div><h4>Map the book</h4><p>Extract the thesis, assumptions, strongest arguments, blind spots, and durable ideas.</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='editorial-card'><div class='num'>02</div><h4>Pressure-test it</h4><p>Switch from friendly conversation to interrogation, skepticism, or academic critique.</p></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='editorial-card'><div class='num'>03</div><h4>Make books collide</h4><p>Compare two books at the level of models and assumptions, not just keyword overlap.</p></div>", unsafe_allow_html=True)

with dna:
    st.markdown("<div class='section-kicker'>Book DNA</div><div class='section-title'>The intellectual fingerprint</div><div class='section-desc'>یک نگاه فشرده به منطق زیرپوستی کتاب؛ نه خلاصه فصل‌به‌فصل.</div>", unsafe_allow_html=True)
    selected = st.selectbox("Choose a book", list(BOOKS), key="dna_book")
    book = BOOKS[selected]
    if st.button("Generate Book DNA", type="primary"):
        st.session_state["dna_ready"] = selected
    if st.session_state.get("dna_ready") == selected:
        c1,c2 = st.columns(2)
        with c1:
            st.markdown(f"<div class='insight-box'><div class='insight-label'>Core thesis</div><div class='insight-value'>{book['thesis']}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='insight-box'><div class='insight-label'>Strongest argument</div><div class='insight-value'>{book['strength']}</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='insight-box'><div class='insight-label'>Hidden assumption</div><div class='insight-value'>{book['assumption']}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='insight-box'><div class='insight-label'>Most vulnerable point</div><div class='insight-value'>{book['weakness']}</div></div>", unsafe_allow_html=True)
        sources_box(book)

with talk:
    st.markdown("<div class='section-kicker'>Conversation</div><div class='section-title'>Talk to a book like a serious counterpart</div><div class='section-desc'>لحن سیستم را عوض کن؛ از گفت‌وگوی عادی تا فشار فکری و نقد آکادمیک.</div>", unsafe_allow_html=True)
    c1, c2 = st.columns([1.15,.85])
    with c1:
        tb = st.selectbox("Book", list(BOOKS), key="talk_book")
    with c2:
        mode = st.selectbox("Mode", ["Talk", "Interrogate", "Skeptical", "Devil's advocate", "Academic critique"])
    st.markdown(f"<span class='mode-pill active'>{mode}</span><span class='mode-pill'>grounded</span><span class='mode-pill'>evidence-linked</span>", unsafe_allow_html=True)
    qs = ["آسیب‌پذیرترین ادعای کتاب چیست؟", "نویسنده چه چیزی را بیش از حد ساده کرده؟", "اگر فقط یک ایده را اجرا کنم کدام است؟"]
    cols = st.columns(3)
    for col, q0 in zip(cols, qs):
        if col.button(q0, use_container_width=True):
            st.session_state["q"] = q0
    q = st.text_input("یا سؤال خودت را بنویس", value=st.session_state.get("q", ""))
    if q:
        with st.chat_message("user"):
            st.write(q)
        with st.chat_message("assistant"):
            st.markdown(talk_answer(tb, mode, q))
            sources_box(BOOKS[tb])

with debate:
    st.markdown("<div class='section-kicker'>Book Debate</div><div class='section-title'>Put two books in the same room</div><div class='section-desc'>جایی که دو مدل فکری واقعاً با هم برخورد می‌کنند.</div>", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        a = st.selectbox("Book A", list(BOOKS), index=0)
    with c2:
        b = st.selectbox("Book B", list(BOOKS), index=1)
    dq = st.text_area("Debate question", value="برای عملکرد بهتر، عادت‌های کوچک مهم‌ترند یا ساختن دوره‌های تمرکز عمیق؟")
    if st.button("Start Debate", type="primary", disabled=a == b):
        st.session_state["debate"] = (a,b,dq)
    if st.session_state.get("debate") == (a,b,dq):
        l,r = st.columns(2)
        with l:
            st.markdown(f"<div class='debate-side'><h4>{a}</h4><p>پایداری رفتار مهم‌تر از شدت مقطعی است. اگر یک رفتار نتواند وارد سیستم روزمره شود، خروجی بلندمدت شکننده می‌ماند. <b>[A1][A2]</b></p></div>", unsafe_allow_html=True)
        with r:
            st.markdown(f"<div class='debate-side'><h4>{b}</h4><p>همه رفتارها ارزش یکسان ندارند؛ leverage و کیفیت توجه تعیین می‌کند کدام فعالیت واقعاً ارزش سیستم‌سازی دارد. <b>[B1][B2]</b></p></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='synthesis'><b>Moderator synthesis</b><br>برای «{dq}» پاسخ قوی‌تر ترکیبی است: ابتدا رفتار با leverage بالا را انتخاب کن، سپس آن را به سیستم تکرارشونده تبدیل کن.</div>", unsafe_allow_html=True)
        with st.expander("Debate evidence"):
            for label, locator, text in [("A1",)+BOOKS[a]["sources"][0][1:], ("A2",)+BOOKS[a]["sources"][1][1:], ("B1",)+BOOKS[b]["sources"][0][1:], ("B2",)+BOOKS[b]["sources"][1][1:]]:
                st.markdown(f"<div class='source'><b>[{label}]</b> · <small>{locator}</small><br>{text}</div>", unsafe_allow_html=True)

st.markdown("<div class='footer'>Bookilink Lab · Product-direction preview · no backend/API required</div>", unsafe_allow_html=True)
