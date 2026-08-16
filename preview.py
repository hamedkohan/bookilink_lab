import streamlit as st

st.set_page_config(page_title="Bookilink Lab Preview", page_icon="◒", layout="wide")

st.markdown("""
<style>
.block-container {max-width: 1120px; padding-top: 1.4rem; padding-bottom: 4rem;}
.hero {padding: 1rem 0 .7rem 0;}
.hero h1 {font-size: 3rem; margin: .1rem 0; letter-spacing: -.04em;}
.hero p {opacity: .7; font-size: 1.05rem;}
.kicker {font-size: .75rem; letter-spacing: .14em; opacity: .55;}
.card {border: 1px solid rgba(128,128,128,.25); border-radius: .9rem; padding: 1rem; min-height: 130px;}
.note {border: 1px solid rgba(128,128,128,.22); border-radius: .8rem; padding: .75rem 1rem; margin-bottom: 1rem;}
</style>
<div class="hero">
<div class="kicker">BOOKILINK / LIVE BROWSER PREVIEW</div>
<h1>Don't just read the book. Enter it.</h1>
<p>Book DNA · Talk / Interrogate · Book Debate</p>
</div>
<div class="note"><b>Demo mode</b> · این preview بدون API و بدون backend اجرا می‌شود و فقط تجربه محصول را نشان می‌دهد.</div>
""", unsafe_allow_html=True)

BOOKS = {
    "Atomic Habits": {
        "author": "James Clear",
        "dna": """### One-line DNA
تغییر پایدار بیشتر از تصمیم‌های بزرگ، حاصل طراحی سیستم‌های کوچک و تکرارشونده است. [S1]

### Core thesis
هدف جهت می‌دهد؛ سیستم رفتار روزمره است که احتمال رسیدن را بالا می‌برد. رفتارهای کوچک با تکرار به evidence برای identity تبدیل می‌شوند. [S1][S2]

### Hidden assumptions
کتاب فرض می‌کند فرد حداقل بخشی از محیط و روتینش را می‌تواند بازطراحی کند. این فرض برای همه موقعیت‌ها یکسان نیست. [S3]

### Strongest argument
اتصال عادت به identity، تغییر را از «کاری که باید انجام بدهم» به «آدمی که دارم می‌شوم» منتقل می‌کند. [S2]

### Most vulnerable point
نقش محدودیت‌های ساختاری و تفاوت‌های فردی گاهی کمتر از حد لازم دیده می‌شود.

### Remember only 3
- رفتار را کوچک کن.
- محیط را به نفعش طراحی کن.
- برای identity موردنظر evidence بساز.
""",
        "sources": [("S1", "chapter 1", "تغییرهای کوچک به‌عنوان ورودی‌های یک سیستم مرکب توضیح داده می‌شوند."), ("S2", "chapter 2", "identity-based habits رفتار تکراری را به تصور فرد از خودش پیوند می‌دهد."), ("S3", "chapter 6", "محیط بخشی از معماری انتخاب و کاهش اصطکاک معرفی می‌شود.")],
    },
    "Deep Work": {
        "author": "Cal Newport",
        "dna": """### One-line DNA
تمرکز بدون حواس‌پرتی روی کار شناختی سخت، یک skill کمیاب و قابل تمرین است. [S1]

### Core thesis
مزیت حرفه‌ای از مشغول بودن نمی‌آید؛ از توانایی تولید خروجی باکیفیت در دوره‌های تمرکز عمیق می‌آید. [S1][S2]

### Hidden assumption
فرد می‌تواند دست‌کم بخشی از تقویم و انتظارات ارتباطی محیط کارش را کنترل کند.

### Strongest argument
Deep work را از preference شخصی به capability اقتصادی تبدیل می‌کند.

### Remember only 3
- زمان عمیق را حفاظت کن.
- shallow work را اندازه بگیر.
- attention را مثل یک skill تمرین کن.
""",
        "sources": [("S1", "introduction", "Deep work فعالیت حرفه‌ای بدون حواس‌پرتی است که ظرفیت شناختی را تا مرز توان می‌برد."), ("S2", "part 1", "کتاب میان busyness و تولید ارزش تمایز می‌گذارد."), ("S3", "rule 2", "تحمل boredom بخشی از بازسازی attention است.")],
    },
    "The Psychology of Money": {
        "author": "Morgan Housel",
        "dna": """### One-line DNA
رفتار مالی خوب بیشتر از دانستن فرمول‌ها، به روان‌شناسی و رابطه ما با risk و uncertainty وابسته است. [S1]

### Core thesis
آدم‌های منطقی می‌توانند تصمیم‌های مالی متفاوتی بگیرند چون تجربه‌های متفاوتی از جهان داشته‌اند. [S1][S2]

### Hidden assumption
ساختن margin of safety و کنترل رفتار شخصی می‌تواند بخشی از عدم‌قطعیت را قابل تحمل کند. [S3]

### Strongest argument
نقش luck و risk را وارد داستان‌های موفقیت می‌کند و جلوی روایت‌های بیش از حد ساده را می‌گیرد. [S2]

### Remember only 3
- room for error بساز.
- آزادی زمانی dividend مهم پول است.
- برنامه‌ای بساز که بتوانی مدت طولانی تحملش کنی.
""",
        "sources": [("S1", "chapter 1", "تجربه شخصی چارچوب متفاوتی برای برداشت از ریسک و پول می‌سازد."), ("S2", "chapters 2–3", "luck و risk در ارزیابی موفقیت و شکست برجسته می‌شوند."), ("S3", "chapter 13", "room for error راهی برای بقا در برابر uncertainty است.")],
    },
}


def sources_box(book, prefix="S"):
    with st.expander("Grounding sources"):
        for i, (_, locator, text) in enumerate(book["sources"], 1):
            st.markdown(f"**[{prefix}{i}] · {locator}**")
            st.write(text)
            st.divider()


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
    st.subheader("Demo library")
    cols = st.columns(3)
    for col, (title, book) in zip(cols, BOOKS.items()):
        with col:
            st.markdown(f"<div class='card'><h3>{title}</h3><div style='opacity:.65'>{book['author']}</div><br><b>Ready for analysis</b></div>", unsafe_allow_html=True)

with dna:
    selected = st.selectbox("Book", list(BOOKS), key="dna_book")
    st.caption("نه summary معمولی؛ thesis، assumptions، strongest/weakest points و takeaways.")
    if st.button("Generate Book DNA", type="primary"):
        st.session_state["dna_ready"] = selected
    if st.session_state.get("dna_ready") == selected:
        st.markdown(BOOKS[selected]["dna"])
        sources_box(BOOKS[selected])

with talk:
    c1, c2 = st.columns(2)
    with c1:
        tb = st.selectbox("Book", list(BOOKS), key="talk_book")
    with c2:
        mode = st.selectbox("Mode", ["Talk", "Interrogate", "Skeptical", "Devil's advocate", "Academic critique"])
    st.markdown("**Try one:**")
    qs = ["آسیب‌پذیرترین ادعای کتاب چیست؟", "نویسنده چه چیزی را بیش از حد ساده کرده؟", "اگر فقط یک ایده را اجرا کنم کدام است؟"]
    cols = st.columns(3)
    for col, q in zip(cols, qs):
        if col.button(q, use_container_width=True):
            st.session_state["q"] = q
    q = st.text_input("یا سؤال خودت را بنویس", value=st.session_state.get("q", ""))
    if q:
        with st.chat_message("user"):
            st.write(q)
        with st.chat_message("assistant"):
            st.markdown(talk_answer(tb, mode, q))
            sources_box(BOOKS[tb])

with debate:
    c1, c2 = st.columns(2)
    with c1:
        a = st.selectbox("Book A", list(BOOKS), index=0)
    with c2:
        b = st.selectbox("Book B", list(BOOKS), index=1)
    dq = st.text_area("What should they debate?", value="برای عملکرد بهتر، عادت‌های کوچک مهم‌ترند یا ساختن دوره‌های تمرکز عمیق؟")
    if st.button("Start Debate", type="primary", disabled=a == b):
        st.session_state["debate"] = (a, b, dq)
    if st.session_state.get("debate") == (a, b, dq):
        st.markdown(f"""## The clash
**{a}** بیشتر از سمت مکانیزم پایداری رفتار وارد می‌شود؛ **{b}** بیشتر می‌پرسد کدام رفتار یا تصمیم ارزش تمرکز و تکرار دارد.

## {a}'s strongest position
Insight بدون سیستم رفتاری پایدار، به outcome مداوم تبدیل نمی‌شود. [A1][A2]

## {b}'s strongest position
همه رفتارها ارزش یکسان ندارند؛ اول باید leverage را پیدا کرد، بعد روی آن سیستم ساخت. [B1][B2]

## Moderator's synthesis
برای سؤال «{dq}» پاسخ قوی‌تر ترکیبی است: **رفتار با leverage بالا را انتخاب کن، بعد آن را به سیستم تکرارشونده تبدیل کن.**
""")
        srcs = [("A1",) + BOOKS[a]["sources"][0][1:], ("A2",) + BOOKS[a]["sources"][1][1:], ("B1",) + BOOKS[b]["sources"][0][1:], ("B2",) + BOOKS[b]["sources"][1][1:]]
        with st.expander("Debate evidence"):
            for label, locator, text in srcs:
                st.markdown(f"**[{label}] · {locator}**")
                st.write(text)
                st.divider()

st.divider()
st.caption("Bookilink Lab browser preview · Demo content only · The full app in app.py includes PDF/EPUB ingestion, embeddings, SQLite retrieval and OpenAI Responses API.")
